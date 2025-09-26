import pytest
from ais_dagger_agents_config import YAMLConfig, CodeMapConfig, ContainerConfig, GitConfig


def test_code_map_config_defaults():
    cfg = YAMLConfig(
        container=ContainerConfig(),
        git=GitConfig(user_name="U", user_email="u@example.com", base_pull_request_branch="main"),
    )
    assert cfg.code_map is not None
    cm = cfg.code_map
    assert cm.out_dir == ".code-map"
    assert cm.max_file_size == 1_000_000
    assert set(cm.languages) >= {"python", "javascript"}
    assert ".git" in cm.ignore_dirs


def test_code_map_config_overrides():
    cfg = YAMLConfig(
        container=ContainerConfig(),
        git=GitConfig(user_name="U", user_email="u@example.com", base_pull_request_branch="main"),
        code_map=CodeMapConfig(out_dir=".map", max_file_size=1234, languages=["python"], ignore_dirs=[".git", "dist"]),
    )
    assert cfg.code_map.out_dir == ".map"
    assert cfg.code_map.max_file_size == 1234
    assert cfg.code_map.languages == ["python"]
    assert cfg.code_map.ignore_dirs == [".git", "dist"]
