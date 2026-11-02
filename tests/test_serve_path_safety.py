"""Unit tests for the internal web UI's path confinement."""

from __future__ import annotations

from pathlib import Path

import pytest

from serve.path_safety import PathSafetyError, resolve_scan_path
from wombat.fixer import restore_backup


def test_relative_path_inside_base_is_allowed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base = tmp_path / "workspace"
    (base / "infra").mkdir(parents=True)
    monkeypatch.setenv("WOMBAT_SCAN_BASE_DIR", str(base))

    assert resolve_scan_path("infra") == (base / "infra").resolve()


def test_absolute_path_outside_base_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base = tmp_path / "workspace"
    base.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.setenv("WOMBAT_SCAN_BASE_DIR", str(base))

    with pytest.raises(PathSafetyError):
        resolve_scan_path(str(outside))


def test_relative_traversal_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base = tmp_path / "workspace"
    base.mkdir()
    (tmp_path / "outside").mkdir()
    monkeypatch.setenv("WOMBAT_SCAN_BASE_DIR", str(base))

    with pytest.raises(PathSafetyError):
        resolve_scan_path("../outside")


def test_symlink_escape_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base = tmp_path / "workspace"
    base.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    link = base / "link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks are not available in this environment")
    monkeypatch.setenv("WOMBAT_SCAN_BASE_DIR", str(base))

    with pytest.raises(PathSafetyError):
        resolve_scan_path("link")


def test_unset_base_defaults_to_working_directory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WOMBAT_SCAN_BASE_DIR", raising=False)
    assert resolve_scan_path(".") == Path.cwd().resolve()


def test_restore_backup_refuses_files_outside_root(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.tf"
    outside.write_text("current")
    outside.with_suffix(".tf.bak").write_text("backup")

    assert restore_backup(outside, root=root) is False
    assert outside.read_text() == "current"


def test_restore_backup_allows_files_inside_root(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    file = root / "main.tf"
    file.write_text("current")
    file.with_suffix(".tf.bak").write_text("original")

    assert restore_backup(file, root=root) is True
    assert file.read_text() == "original"
