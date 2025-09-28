"""Language detection utilities for code parsing."""

import re
from typing import Optional, Dict

# Extension to language mapping
EXTENSION_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".cs": "c_sharp",
    ".rb": "ruby",
    ".php": "php",
}

# Shebang patterns
SHEBANG_PATTERNS = {
    r"python[0-9.]*": "python",
    r"node": "javascript",
    r"bash|sh": "bash",
    r"ruby": "ruby",
    r"php": "php",
}


def detect_language(
    path: str, 
    text_head: str, 
    overrides: Optional[Dict[str, str]] = None
) -> Optional[str]:
    """Detect language from file path and content.
    
    Args:
        path: File path (for extension)
        text_head: First ~8KB of file content
        overrides: Custom extension mappings (e.g., {".tsx": "typescript"})
    
    Returns:
        Language name or None if not detected
    """
    # Apply overrides first
    if overrides:
        for ext, lang in overrides.items():
            if path.endswith(ext):
                return lang
    
    # Extension-based detection
    for ext, lang in EXTENSION_MAP.items():
        if path.endswith(ext):
            return lang
    
    # Shebang detection
    if text_head.startswith("#!"):
        first_line = text_head.split("\n")[0].lower()
        for pattern, lang in SHEBANG_PATTERNS.items():
            if re.search(pattern, first_line):
                return lang
    
    # Modeline detection (vim/emacs)
    lines = text_head.split("\n")[:5]  # Check first few lines
    for line in lines:
        line = line.lower()
        # vim: ft=python or vim: filetype=python
        vim_match = re.search(r"vim?:\s*(?:ft|filetype)=([a-z]+)", line)
        if vim_match:
            lang = vim_match.group(1)
            if lang in EXTENSION_MAP.values():
                return lang
        
        # emacs: -*- python -*-
        emacs_match = re.search(r"-\*-.*?([a-z]+).*?-\*-", line)
        if emacs_match:
            lang = emacs_match.group(1)
            if lang in EXTENSION_MAP.values():
                return lang
    
    # Lightweight keyword heuristics (best-effort)
    if "def " in text_head or "import " in text_head or "class " in text_head:
        return "python"
    if "function " in text_head or "const " in text_head or "let " in text_head:
        return "javascript"
    if "interface " in text_head or "type " in text_head:
        return "typescript"
    
    return None
