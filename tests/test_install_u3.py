"""U3 — Clean <= 3-command installation experience, cross-OS dry-run mode, and installation guide accuracy."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL_SH = ROOT / "scripts" / "install.sh"
INSTALL_PS1 = ROOT / "scripts" / "install.ps1"


def _make_clean_project(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    proj = tmp_path / "proj"
    home = tmp_path / "home"
    bin_dir = tmp_path / "bin"
    invocations = tmp_path / "invocations.log"
    invocations.write_text("", encoding="utf-8")

    for d in (proj / "scripts", proj / "web" / "dist", home / ".local" / "bin", bin_dir):
        d.mkdir(parents=True)
    (proj / "web" / "dist" / "index.html").write_text("<html></html>", encoding="utf-8")
    sh = proj / "scripts" / "install.sh"
    sh.write_text(INSTALL_SH.read_text(encoding="utf-8"), encoding="utf-8")
    sh.chmod(0o755)

    (bin_dir / "python3").symlink_to(sys.executable)

    fake_pipx = bin_dir / "pipx"
    fake_pipx.write_text(
        "#!/bin/sh\n"
        'echo "pipx $*" >> "$INV_LOG"\n'
        'if [ "$1" = "environment" ]; then echo "$FAKE_BIN"; fi\n',
        encoding="utf-8",
    )
    fake_pipx.chmod(0o755)

    fake_llama = bin_dir / "llama-server"
    fake_llama.write_text("#!/bin/sh\necho 'version: 0.0.0 (fake)'\n", encoding="utf-8")
    fake_llama.chmod(0o755)

    fake_spike = home / ".local" / "bin" / "spike"
    fake_spike.write_text(
        "#!/bin/sh\n"
        'echo "spike $*" >> "$INV_LOG"\n'
        'exec "$REAL_PY" -c "import sys; from spike.cli import main; sys.exit(main())" "$@"\n',
        encoding="utf-8",
    )
    fake_spike.chmod(0o755)
    return proj, home, bin_dir, invocations


def test_install_sh_dry_run_executes_nothing_and_leaves_home_clean(tmp_path: Path) -> None:
    proj, home, bin_dir, invocations = _make_clean_project(tmp_path)
    bash = shutil.which("bash")
    assert bash is not None

    env = {
        "HOME": str(home),
        "SPIKE_HOME": str(home / ".spike"),
        "PATH": f"{bin_dir}:/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "PYTHONPATH": str(ROOT),
        "SPIKE_NO_KEYRING": "1",
        "REAL_PY": sys.executable,
        "FAKE_BIN": str(home / ".local" / "bin"),
        "INV_LOG": str(invocations),
    }
    res = subprocess.run(
        [bash, str(proj / "scripts" / "install.sh"), "--dry-run"],
        cwd=proj,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert res.returncode == 0, res.stdout + res.stderr
    assert "[dry-run]" in res.stdout
    assert "models pull qwen3.5-4b" in res.stdout
    assert "doctor --strict" in res.stdout
    # Only `pipx environment` read-only lookup is allowed; no `pipx install` or `spike` run may happen
    logged = invocations.read_text(encoding="utf-8").splitlines()
    assert not any(line.startswith("pipx install") for line in logged), logged
    assert not any(line.startswith("spike ") for line in logged), logged
    assert not (home / ".spike").exists()


def test_install_sh_clean_no_model_runs_real_spike_doctor_on_any_posix_os(tmp_path: Path) -> None:
    proj, home, bin_dir, invocations = _make_clean_project(tmp_path)
    bash = shutil.which("bash")
    assert bash is not None

    env = {
        "HOME": str(home),
        "SPIKE_HOME": str(home / ".spike"),
        "PATH": f"{bin_dir}:/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "PYTHONPATH": str(ROOT),
        "SPIKE_NO_KEYRING": "1",
        "REAL_PY": sys.executable,
        "FAKE_BIN": str(home / ".local" / "bin"),
        "INV_LOG": str(invocations),
    }
    res = subprocess.run(
        [bash, str(proj / "scripts" / "install.sh"), "--yes", "--no-model"],
        cwd=proj,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert res.returncode == 0, res.stdout + res.stderr
    assert "Skipping the model download (--no-model)." in res.stdout
    assert "Done. Start SPIKE with:" in res.stdout
    logged = invocations.read_text(encoding="utf-8")
    assert "spike doctor --strict --no-model-check" in logged
    assert "models pull" not in logged


def test_install_ps1_supports_dry_run_and_stays_ascii() -> None:
    raw = INSTALL_PS1.read_bytes()
    text = raw.decode("ascii")
    assert "[switch]$DryRun" in text
    assert "[dry-run]" in text


def test_installation_guides_use_real_script_and_test_paths() -> None:
    for lang in ("en", "es"):
        page = ROOT / "docs" / "guide" / lang / "installation.md"
        text = page.read_text(encoding="utf-8")
        assert "scripts/install.sh" in text
        assert "scripts\\install.ps1" in text
        assert "--dry-run" in text
        assert "./install.sh" not in text
        # Every referenced tests/test_*.py file must actually exist
        referenced_tests = re.findall(r"tests/test_[a-zA-Z0-9_]+\.py", text)
        assert referenced_tests, f"No test files referenced in {lang}/installation.md"
        for rel in referenced_tests:
            assert (ROOT / rel).is_file(), f"Non-existent test {rel!r} cited in {lang}/installation.md"
