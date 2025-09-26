from __future__ import annotations

import os
import sys
import json
import time
import shlex
import asyncio
import tempfile
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_IGNORED_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "out",
    "target",
    "__pycache__",
    ".venv",
    "vendor",
    "coverage",
    "htmlcov",
}

MAX_FILE_SIZE_BYTES = 1_000_000  # 1MB
DEFAULT_TIMEOUT_SECONDS = 120

@dataclass
class FileTreeNode:
    name: str
    type: str  # 'file' | 'directory'
    filePath: str
    lastReadTime: Optional[float] = None
    children: Optional[List["FileTreeNode"]] = None

@dataclass
class ProjectFileContext:
    projectRoot: str
    cwd: str
    fileTree: List[FileTreeNode]
    fileTokenScores: Dict[str, Dict[str, float]]
    tokenCallers: Optional[Dict[str, Dict[str, List[str]]]] = None
    knowledgeFiles: Dict[str, str] = field(default_factory=dict)
    userKnowledgeFiles: Optional[Dict[str, str]] = None
    agentTemplates: Dict[str, Any] = field(default_factory=dict)
    customToolDefinitions: Dict[str, Any] = field(default_factory=dict)
    codebuffConfig: Optional[Dict[str, Any]] = None
    gitChanges: Dict[str, str] = field(default_factory=lambda: {
        "status": "",
        "diff": "",
        "diffCached": "",
        "lastCommitMessages": "",
    })
    changesSinceLastChat: Dict[str, str] = field(default_factory=dict)
    shellConfigFiles: Dict[str, str] = field(default_factory=dict)
    systemInfo: Dict[str, Any] = field(default_factory=lambda: {
        "platform": sys.platform,
        "shell": os.environ.get("SHELL", ""),
        "nodeVersion": os.environ.get("NODE_VERSION", ""),
        "arch": os.uname().machine if hasattr(os, "uname") else "",
        "homedir": os.path.expanduser("~"),
        "cpus": os.cpu_count() or 0,
    })

# Cache
_cached_context: Optional[ProjectFileContext] = None
_cached_root: Optional[str] = None
_cached_paths_hash: Optional[str] = None


def _is_binary_file(path_: str) -> bool:
    try:
        with open(path_, "rb") as f:
            chunk = f.read(512)
        return b"\x00" in chunk
    except Exception:
        return False


def get_project_file_tree(project_root: str, max_files: int = 10_000, max_depth: int = 20) -> List[FileTreeNode]:
    nodes: List[FileTreeNode] = []
    root_name = os.path.basename(os.path.abspath(project_root))

    def walk(dir_path: str, rel_path: str, depth: int) -> Optional[FileTreeNode]:
        if depth > max_depth:
            return None
        try:
            entries = os.listdir(dir_path)
        except Exception:
            return None
        children: List[FileTreeNode] = []
        for name in entries:
            if len(nodes) >= max_files:
                break
            full = os.path.join(dir_path, name)
            rel = os.path.join(rel_path, name) if rel_path else name
            try:
                st = os.stat(full)
            except Exception:
                continue
            if os.path.isdir(full):
                if name in DEFAULT_IGNORED_DIRS:
                    continue
                child = walk(full, rel, depth + 1)
                if child and child.children:
                    children.append(child)
            else:
                if st.st_size > MAX_FILE_SIZE_BYTES:
                    continue
                if _is_binary_file(full):
                    continue
                node = FileTreeNode(name=name, type="file", filePath=rel, lastReadTime=st.st_atime)
                nodes.append(node)
                children.append(node)
        return FileTreeNode(name=os.path.basename(dir_path) if rel_path else root_name, type="directory", filePath=rel_path, children=children)

    root = walk(project_root, "", 0)
    return root.children if root and root.children else []


def flatten_tree(nodes: List[FileTreeNode]) -> List[FileTreeNode]:
    out: List[FileTreeNode] = []
    for n in nodes:
        if n.type == "file":
            out.append(n)
        elif n.children:
            out.extend(flatten_tree(n.children))
    return out


def _hash_paths(paths: List[str]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(p.encode())
    return h.hexdigest()


async def _detect_runtime() -> Optional[str]:
    async def which(cmd: str) -> bool:
        proc = await asyncio.create_subprocess_shell(
            f"which {shlex.quote(cmd)}",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.communicate()
        return proc.returncode == 0

    if await which("bun"):
        return "bun"
    if await which("npx"):
        return "npx"
    if await which("node"):
        return "node"
    return None


async def _run_cmd(cmd: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> Tuple[int, str, str]:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        outs, errs = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return proc.returncode or 0, (outs or b"").decode("utf-8", "ignore"), (errs or b"").decode("utf-8", "ignore")
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except Exception:
            pass
        return 124, "", "timeout"


async def get_file_token_scores_via_cli(project_root: str, all_file_paths: List[str]) -> Tuple[Dict[str, Dict[str, float]], Optional[Dict[str, Dict[str, List[str]]]]]:
    if not all_file_paths:
        return {}, {}

    runtime = await _detect_runtime()
    # Compute local TS CLI path for Bun fallback
    here = os.path.dirname(os.path.abspath(__file__))
    cli_ts = os.path.normpath(os.path.join(here, "../../codebuff/packages/code-map/src/cli.ts"))
    bun_bin_local = os.path.normpath(os.path.join(here, "../../.bin/bun"))

    with tempfile.TemporaryDirectory() as tmpd:
        paths_file = os.path.join(tmpd, "filelist.txt")
        out_file = os.path.join(tmpd, "tokens.json")
        with open(paths_file, "w", encoding="utf-8") as f:
            f.write("\n".join(all_file_paths))

        cmd_candidates: List[str] = []
        if runtime == "bun":
            cmd_candidates.append(f"bun x code-map tokens --root {shlex.quote(project_root)} --paths @{shlex.quote(paths_file)} --out {shlex.quote(out_file)}")
            cmd_candidates.append(f"bun {shlex.quote(cli_ts)} tokens --root {shlex.quote(project_root)} --paths @{shlex.quote(paths_file)} --out {shlex.quote(out_file)}")
            cmd_candidates.append(f"{shlex.quote(bun_bin_local)} {shlex.quote(cli_ts)} tokens --root {shlex.quote(project_root)} --paths @{shlex.quote(paths_file)} --out {shlex.quote(out_file)}")
        if runtime == "npx":
            cmd_candidates.append(f"npx --yes code-map tokens --root {shlex.quote(project_root)} --paths @{shlex.quote(paths_file)} --out {shlex.quote(out_file)}")
        if runtime == "node" or not cmd_candidates:
            # No reliable CLI; graceful fallback
            return {}, {}

        for cmd in cmd_candidates:
            rc, _stdout, _stderr = await _run_cmd(cmd)
            if rc == 0:
                try:
                    with open(out_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    token_scores = data.get("tokenScores") or {}
                    token_callers = data.get("tokenCallers") or {}
                    if not isinstance(token_scores, dict):
                        return {}, {}
                    return token_scores, token_callers
                except Exception:
                    return {}, {}
        # All attempts failed
        return {}, {}


async def get_project_file_context(project_root: str, last_file_version: Dict[str, str] | None = None) -> ProjectFileContext:
    global _cached_context, _cached_root, _cached_paths_hash

    file_tree = get_project_file_tree(project_root)
    all_paths = [n.filePath for n in flatten_tree(file_tree) if n.type == "file"]

    paths_hash = _hash_paths(all_paths)
    reuse_cache = (
        _cached_context is not None and _cached_root == project_root and _cached_paths_hash == paths_hash
    )

    if reuse_cache:
        return _cached_context  # type: ignore

    token_scores, token_callers = await get_file_token_scores_via_cli(project_root, all_paths)

    ctx = ProjectFileContext(
        projectRoot=project_root,
        cwd=project_root,
        fileTree=file_tree,
        fileTokenScores=token_scores,
        tokenCallers=token_callers,
        knowledgeFiles={},
        userKnowledgeFiles={},
        agentTemplates={},
        customToolDefinitions={},
        codebuffConfig=None,
        gitChanges={"status": "", "diff": "", "diffCached": "", "lastCommitMessages": ""},
        changesSinceLastChat={},
        shellConfigFiles={},
    )

    _cached_context = ctx
    _cached_root = project_root
    _cached_paths_hash = paths_hash
    return ctx
