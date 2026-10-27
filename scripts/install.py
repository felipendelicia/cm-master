#!/usr/bin/env python3
"""Copy the portable skill into one host's discovery directory."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile


def install(source, destination):
    # Keep the final component unresolved so dangling symlinks are rejected too.
    destination = destination.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"El destino ya existe; no se sobrescribió: {destination}")
    if not (source / "SKILL.md").is_file():
        raise ValueError("No se encontró la skill fuente junto al instalador.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".cm-master-install-", dir=destination.parent) as temporary:
        staged = Path(temporary) / "cm-master"
        shutil.copytree(source, staged, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
        # mkdir is the exclusive reservation; it never replaces an existing installation.
        destination.mkdir()
        try:
            for child in staged.iterdir():
                shutil.move(str(child), str(destination / child.name))
        except BaseException:
            shutil.rmtree(destination)
            raise
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("codex", "claude"), required=True)
    parser.add_argument("--destination", type=Path, help="Carpeta final de la skill; para pruebas o instalación de proyecto.")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / "skills/cm-master"
    base = ".agents" if args.host == "codex" else ".claude"
    destination = args.destination or Path.home() / base / "skills/cm-master"
    try:
        path = install(source, destination)
        print(json.dumps({"host": args.host, "installed": str(path), "notice": "No se modificaron permisos, cuentas ni tareas."}, ensure_ascii=False))
        return 0
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
