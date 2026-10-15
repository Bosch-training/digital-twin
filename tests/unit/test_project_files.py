import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_skeleton_files_exist():
    for rel in ("app/__init__.py", "app/main.py", "requirements.txt", ".gitignore"):
        assert (ROOT / rel).is_file(), rel
    for rel in ("tests/unit", "tests/api"):
        assert (ROOT / rel).is_dir(), rel


def test_requirements_are_pinned():
    lines = [
        line.strip()
        for line in (ROOT / "requirements.txt").read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    assert lines
    assert all(re.fullmatch(r"[A-Za-z0-9_.\[\]-]+==[\w.]+", line) for line in lines), lines


def test_gitignore_excludes_env_files():
    assert ".env" in (ROOT / ".gitignore").read_text().splitlines()
