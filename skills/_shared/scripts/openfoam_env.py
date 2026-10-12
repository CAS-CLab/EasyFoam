"""Cross-platform OpenFOAM Foundation v13 discovery and command construction.

Windows hosts execute OpenFOAM through WSL. Linux and WSL sessions execute it
natively. Set ``EASYFOAM_EXEC_BACKEND`` to ``auto`` (default), ``wsl``, or
``native``. ``EASYFOAM_OPENFOAM_BASHRC`` may point to the OpenFOAM bashrc path
visible inside the selected shell.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

BACKENDS = ("auto", "wsl", "native")
DEFAULT_BASHRC_CANDIDATES = (
    "/opt/openfoam13/etc/bashrc",
    "/usr/lib/openfoam/openfoam13/etc/bashrc",
    "/usr/local/openfoam13/etc/bashrc",
)


def resolve_backend(requested: str | None = None) -> str:
    backend = (requested or os.environ.get("EASYFOAM_EXEC_BACKEND") or "auto").strip().lower()
    if backend not in BACKENDS:
        raise ValueError(f"unsupported EasyFoam execution backend: {backend}")
    if backend == "auto":
        return "wsl" if os.name == "nt" else "native"
    return backend


def _wsl_path(path: Path) -> str:
    resolved = path.resolve(strict=True)
    if not shutil.which("wsl"):
        raise RuntimeError("WSL executable is unavailable")
    completed = subprocess.run(
        ["wsl", "wslpath", "-a", str(resolved)],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=15,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        raise RuntimeError(completed.stderr.strip() or f"cannot convert Windows path for WSL: {resolved}")
    return completed.stdout.strip()


def _bootstrap_script() -> str:
    configured = os.environ.get("EASYFOAM_OPENFOAM_BASHRC", "").strip()
    if configured:
        prefix = f"easyfoam_bashrc={shlex.quote(configured)}"
    else:
        candidates = " ".join(shlex.quote(item) for item in DEFAULT_BASHRC_CANDIDATES)
        prefix = (
            "easyfoam_bashrc=''; "
            f"for candidate in {candidates}; do "
            "if [ -f \"$candidate\" ]; then easyfoam_bashrc=\"$candidate\"; break; fi; "
            "done"
        )
    return (
        prefix
        + "; test -n \"$easyfoam_bashrc\" || { echo 'OpenFOAM bashrc was not found. Set EASYFOAM_OPENFOAM_BASHRC.' >&2; exit 127; }"
        + "; test -f \"$easyfoam_bashrc\" || { echo \"OpenFOAM bashrc does not exist: $easyfoam_bashrc\" >&2; exit 127; }"
        + "; source \"$easyfoam_bashrc\""
    )


def build_openfoam_command(
    command: list[str],
    cwd: Path | None = None,
    backend: str | None = None,
) -> list[str]:
    """Return the host argv used to execute one OpenFOAM command."""
    if not command:
        raise ValueError("OpenFOAM command must not be empty")
    selected = resolve_backend(backend)
    if selected == "wsl":
        if os.name != "nt":
            raise RuntimeError("the wsl backend is supported only from a Windows host")
        if not shutil.which("wsl"):
            raise RuntimeError("WSL executable is unavailable")
        shell_cwd = _wsl_path(cwd) if cwd else None
        shell = ["wsl", "bash", "-lc"]
    else:
        if not shutil.which("bash"):
            raise RuntimeError("bash executable is unavailable for the native backend")
        shell_cwd = str(cwd.resolve(strict=True)) if cwd else None
        shell = ["bash", "-lc"]
    prefix = f"cd {shlex.quote(shell_cwd)} && " if shell_cwd else ""
    return shell + [prefix + _bootstrap_script() + " && " + shlex.join(command)]


def discover(backend: str | None = None) -> dict[str, object]:
    selected = resolve_backend(backend)
    script = _bootstrap_script() + r'''
printf 'EASYFOAM_BASHRC=%s\n' "$easyfoam_bashrc"
printf 'WM_PROJECT=%s\n' "${WM_PROJECT:-}"
printf 'WM_PROJECT_VERSION=%s\n' "${WM_PROJECT_VERSION:-}"
printf 'FOAM_VERSION=%s\n' "$(foamVersion 2>/dev/null || true)"
for cmd in foamRun blockMesh checkMesh foamPostProcess; do
    printf '%s=%s\n' "$cmd" "$(command -v "$cmd" 2>/dev/null || true)"
done
'''
    try:
        if selected == "wsl":
            if os.name != "nt" or not shutil.which("wsl"):
                return {"available": False, "backend": selected, "reason": "WSL is unavailable on this host"}
            argv = ["wsl", "bash", "-lc", script]
        else:
            if not shutil.which("bash"):
                return {"available": False, "backend": selected, "reason": "bash is unavailable"}
            argv = ["bash", "-lc", script]
        completed = subprocess.run(
            argv,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": False, "backend": selected, "reason": str(exc)}
    if completed.returncode != 0:
        return {
            "available": False,
            "backend": selected,
            "reason": completed.stderr.strip() or "OpenFOAM bootstrap failed",
        }
    values: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    version_text = values.get("WM_PROJECT_VERSION") or values.get("FOAM_VERSION") or ""
    match = re.search(r"(\d+)$", version_text)
    version = match.group(1) if match else None
    paths = {name: values.get(name, "") for name in ("foamRun", "blockMesh", "checkMesh", "foamPostProcess")}
    required = ("foamRun", "blockMesh", "checkMesh")
    if not all(paths[name] for name in required):
        missing = [name for name in required if not paths[name]]
        return {
            "available": False,
            "backend": selected,
            "platform": platform.system().lower(),
            "openfoam_version": version,
            "bashrc": values.get("EASYFOAM_BASHRC") or None,
            "paths": paths,
            "reason": "required OpenFOAM commands are unavailable: " + ", ".join(missing),
        }
    return {
        "available": True,
        "backend": selected,
        "platform": platform.system().lower(),
        "wm_project": values.get("WM_PROJECT") or None,
        "openfoam_version": version,
        "bashrc": values.get("EASYFOAM_BASHRC") or None,
        "paths": paths,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["discover", "exec"])
    parser.add_argument("--backend", choices=BACKENDS, default=None)
    parser.add_argument("--cwd", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.action == "discover":
        result = discover(args.backend)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("available") else 1
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    completed = subprocess.run(
        build_openfoam_command(command, args.cwd, args.backend),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    print(completed.stdout, end="")
    print(completed.stderr, end="", file=sys.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
