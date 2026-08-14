#!/usr/bin/env python3
"""Create a music Web wallpaper from the bundled starter."""

from __future__ import annotations

import argparse
import html
import json
import shutil
import sys
from pathlib import Path


PLACEHOLDERS = ("{{TITLE}}", "{{AUTHOR}}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="New wallpaper directory")
    parser.add_argument("--title", required=True, help="Wallpaper title")
    parser.add_argument("--author", required=True, help="Actual wallpaper author")
    return parser.parse_args()


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


def validate_label(value: str, field: str) -> str:
    value = value.strip()
    if not value:
        raise SystemExit(f"{field} cannot be empty")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise SystemExit(f"{field} cannot contain line breaks or control characters")
    return value


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")


def markdown_escape(value: str) -> str:
    for character in ("\\", "`", "*", "_", "[", "]", "<", ">", "|"):
        value = value.replace(character, f"\\{character}")
    return value


def apply_metadata(target: Path, title: str, author: str) -> None:
    project_path = target / "project.json"
    project = json.loads(project_path.read_text(encoding="utf-8"))
    project["title"] = title
    write_text(project_path, json.dumps(project, ensure_ascii=False, indent=2) + "\n")

    catalog_path = target / "static" / "js" / "catalog.js"
    catalog = catalog_path.read_text(encoding="utf-8")
    catalog = catalog.replace('"{{TITLE}}"', json.dumps(title, ensure_ascii=False))
    catalog = catalog.replace('"{{AUTHOR}}"', json.dumps(author, ensure_ascii=False))
    write_text(catalog_path, catalog)

    index_path = target / "index.html"
    index = index_path.read_text(encoding="utf-8")
    index = index.replace("{{TITLE}}", html.escape(title, quote=True))
    index = index.replace("{{AUTHOR}}", html.escape(author, quote=True))
    write_text(index_path, index)

    sources_path = target / "SOURCES.md"
    sources = sources_path.read_text(encoding="utf-8")
    sources = sources.replace("{{TITLE}}", markdown_escape(title))
    sources = sources.replace("{{AUTHOR}}", markdown_escape(author))
    write_text(sources_path, sources)

    leftovers = []
    for path in target.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".js", ".json", ".md"}:
            continue
        content = path.read_text(encoding="utf-8")
        if any(placeholder in content for placeholder in PLACEHOLDERS):
            leftovers.append(path.relative_to(target).as_posix())
    if leftovers:
        raise SystemExit(f"Unreplaced metadata placeholders remain: {', '.join(leftovers)}")


def main() -> int:
    configure_console()
    args = parse_args()
    title = validate_label(args.title, "Wallpaper title")
    author = validate_label(args.author, "Wallpaper author")
    target = args.target.resolve()
    starter = Path(__file__).resolve().parents[1] / "assets" / "starter"

    if not starter.is_dir():
        raise SystemExit(f"Starter directory is missing: {starter}")
    if target.exists() and any(target.iterdir()):
        raise SystemExit(f"Target must be absent or empty: {target}")

    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(starter, target, dirs_exist_ok=True)
    apply_metadata(target, title, author)

    for relative in ("assets/audio", "assets/lyrics", "assets/covers", "assets/logos"):
        (target / relative).mkdir(parents=True, exist_ok=True)

    print(f"Created music Web wallpaper: {target}")
    print("Next: add authorized media, edit static/js/catalog.js, update SOURCES.md, and validate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
