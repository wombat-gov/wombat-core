"""Integration tests for Wombat validation CLI commands and flags."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from wombat.cli import app

try:
    import reportlab  # noqa: F401
    _REPORTLAB_AVAILABLE = True
except ImportError:  # pragma: no cover
    _REPORTLAB_AVAILABLE = False


runner = CliRunner()


@pytest.fixture
def sample_result(tmp_path: Path):
    """Create a minimal wombat-result.json for validation tests."""
    result = {
        "schema_version": "1.0",
        "project": "test-project",
        "branch": "main",
        "git_sha": "abc1234",
        "triggered_by": "local",
        "run": {"is_cicd": False},
        "iac_framework": "terraform",
        "stage": "prod",
        "score": 87,
        "pillar_scores": {"SEC": 90},
        "path": "infra/",
        "controls_loaded": 10,
        "controls_run": 10,
        "detected_regions": [],
        "source_paths": ["infra/"],
        "controls_meta": [],
        "findings": [],
        "secret_findings": [],
    }
    path = tmp_path / "wombat-result.json"
    path.write_text(json.dumps(result), encoding="utf-8")
    return path


@pytest.fixture
def key_path(tmp_path: Path):
    """Return a path for a generated validation key."""
    return tmp_path / "validation.key"


def test_validate_offline_creates_envelope_and_badge(
    tmp_path: Path, sample_result: Path, key_path: Path
):
    """`wombat validate offline` produces an envelope, badge JSON, badge SVG, and PDF certificate."""
    output_dir = tmp_path / "out"
    result = runner.invoke(
        app,
        [
            "validate",
            "offline",
            str(sample_result),
            "--key",
            str(key_path),
            "--output-dir",
            str(output_dir),
        ],
    )
    assert result.exit_code == 0, result.output

    files = {p.name for p in output_dir.iterdir()}
    assert any(n.startswith("wombat-validation-") for n in files)
    assert any(n.startswith("wombat-badge-") and n.endswith(".json") for n in files)
    assert any(n.startswith("wombat-badge-") and n.endswith(".svg") for n in files)
    if _REPORTLAB_AVAILABLE:
        assert any(n.startswith("wombat-certificate-") and n.endswith(".pdf") for n in files)


def test_validate_offline_envelope_is_verifiable(
    tmp_path: Path, sample_result: Path, key_path: Path
):
    """An offline envelope passes `wombat verify`."""
    output_dir = tmp_path / "out"
    runner.invoke(
        app,
        [
            "validate",
            "offline",
            str(sample_result),
            "--key",
            str(key_path),
            "--output-dir",
            str(output_dir),
        ],
    )

    envelope = next(output_dir.glob("wombat-validation-*.json"))
    result = runner.invoke(app, ["verify", str(envelope)])
    assert result.exit_code == 0, result.output
    assert "verification passed" in result.output.lower()


def test_validate_official_fails_without_server(
    tmp_path: Path, sample_result: Path, key_path: Path
):
    """`wombat validate official` fails gracefully when no server is configured."""
    cert_path = tmp_path / "dummy-cert.pem"
    cert_path.write_text("dummy", encoding="utf-8")
    output_dir = tmp_path / "out"
    cert_path = tmp_path / "server.pem"
    cert_path.write_text("-----BEGIN CERTIFICATE-----\nDUMMY\n-----END CERTIFICATE-----\n")
    result = runner.invoke(
        app,
        [
            "validate",
            "official",
            str(sample_result),
            "--key",
            str(key_path),
            "--output-dir",
            str(output_dir),
            "--validation-url",
            "http://127.0.0.1:1",  # unreachable
            "--server-certificate",
            str(cert_path),
        ],
    )
    assert result.exit_code != 0
    assert "cannot reach validation server" in result.output.lower()


def test_validate_official_with_fallback_to_offline(
    tmp_path: Path, sample_result: Path, key_path: Path
):
    """--skip-validation-on-offline style fallback is handled by the CLI path.

    The top-level command path in wombat check has the fallback flag; here we
    test that the helper itself creates an offline envelope when fallback is True.
    """
    from wombat.attestation import create_offline_envelope
    from wombat.validation_cli import _request_official_validation
    from rich.console import Console

    rc = Console()
    key_path.parent.mkdir(parents=True, exist_ok=True)

    from wombat.schema import WombatResultSchema

    result = WombatResultSchema.model_validate_json(sample_result.read_text())
    envelope = _request_official_validation(
        result,
        key_path,
        tmp_path / "out",
        api_key=None,
        server_url="http://127.0.0.1:1",
        server_certificate="dummy",
        rc=rc,
        fallback_on_offline=True,
    )
    assert envelope is not None
    assert envelope.status == "offline"


def test_verify_detects_tampered_envelope(
    tmp_path: Path, sample_result: Path, key_path: Path
):
    """`wombat verify` fails when the result inside the envelope is tampered."""
    output_dir = tmp_path / "out"
    runner.invoke(
        app,
        [
            "validate",
            "offline",
            str(sample_result),
            "--key",
            str(key_path),
            "--output-dir",
            str(output_dir),
        ],
    )

    envelope = next(output_dir.glob("wombat-validation-*.json"))
    data = json.loads(envelope.read_text())
    data["result"]["score"] = 99
    envelope.write_text(json.dumps(data), encoding="utf-8")

    result = runner.invoke(app, ["verify", str(envelope)])
    assert result.exit_code != 0
    assert "failed" in result.output.lower()


def test_check_requires_output_json_for_validation(key_path: Path):
    """`wombat check --validate` requires `--output json`."""
    # We don't need a real scan; the flag check happens before parsing.
    result = runner.invoke(
        app,
        [
            "check",
            "tests/fixtures/compliant",
            "--validate",
            "offline",
            "--validation-key",
            str(key_path),
            "--controls-dir",
            "controls",
        ],
    )
    assert result.exit_code == 2
    assert "--validate requires --output json" in result.output


def test_validate_generate_key_creates_key(tmp_path: Path):
    """`wombat validate generate-key` writes a new Ed25519 private key."""
    key = tmp_path / "new.key"
    result = runner.invoke(app, ["validate", "generate-key", "--path", str(key)])
    assert result.exit_code == 0, result.output
    assert key.exists()
    assert "generated" in result.output.lower()


def test_validate_generate_key_refuses_overwrite(tmp_path: Path, key_path: Path):
    """`wombat validate generate-key` refuses to overwrite an existing key."""
    key_path.write_text("existing", encoding="utf-8")
    result = runner.invoke(app, ["validate", "generate-key", "--path", str(key_path)])
    assert result.exit_code == 1
    assert "already exists" in result.output.lower()


def test_validate_show_displays_summary(
    tmp_path: Path, sample_result: Path, key_path: Path
):
    """wombat validate show prints a validation summary."""
    output_dir = tmp_path / "out"
    runner.invoke(
        app,
        [
            "validate",
            "offline",
            str(sample_result),
            "--key",
            str(key_path),
            "--output-dir",
            str(output_dir),
        ],
    )
    envelope = next(output_dir.glob("wombat-validation-*.json"))
    result = runner.invoke(app, ["validate", "show", str(envelope)])
    assert result.exit_code == 0, result.output
    assert "offline" in result.output.lower()
