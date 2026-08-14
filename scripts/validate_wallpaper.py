#!/usr/bin/env python3
"""Validate a music Web wallpaper's structure, catalog, paths, credits, and release readiness."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


REFERENCE_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id=2905017768"
SKILL_AUTHOR = "双料贝斯手长崎素世"
SKILL_EMAIL = "2932821663@qq.com"
PLACEHOLDER = re.compile(r"\{\{[A-Z][A-Z0-9_-]*\}\}")
MEDIA_SUFFIXES = {
    ".mp3", ".wav", ".flac", ".m4a", ".ogg", ".opus", ".aac",
    ".lrc", ".txt", ".srt", ".vtt",
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".bmp", ".avif",
    ".ttf", ".otf", ".woff", ".woff2",
}


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Wallpaper project directory")
    parser.add_argument("--release", action="store_true", help="Apply stricter release checks")
    return parser.parse_args()


def load_catalog(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"=\s*(\{.*\})\s*;?\s*$", text, flags=re.DOTALL)
    if not match:
        raise ValueError("catalog.js must assign one JSON object")
    value = json.loads(match.group(1))
    if not isinstance(value, dict):
        raise ValueError("catalog root must be an object")
    return value


def safe_project_path(root: Path, value: object, label: str, errors: list[str], require_file: bool = True) -> tuple[Path, str] | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty relative path")
        return None
    raw = value.strip().replace("\\", "/")
    if "\x00" in raw or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", raw):
        errors.append(f"{label} must not be an absolute path or URL: {value}")
        return None
    relative = Path(raw)
    if relative.is_absolute():
        errors.append(f"{label} must be project-relative: {value}")
        return None
    candidate = (root / relative).resolve()
    try:
        normalized = candidate.relative_to(root).as_posix()
    except ValueError:
        errors.append(f"{label} escapes the wallpaper project: {value}")
        return None
    if require_file and not candidate.is_file():
        errors.append(f"{label} does not exist: {value}")
    return candidate, normalized


def list_records(value: object, label: str, errors: list[str]) -> list[dict]:
    if not isinstance(value, list):
        errors.append(f"catalog {label} must be an array")
        return []
    result = []
    for index, item in enumerate(value):
        if isinstance(item, dict):
            result.append(item)
        else:
            errors.append(f"{label}[{index}] must be an object")
    return result


def record_ids(records: list[dict], label: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    for index, record in enumerate(records):
        record_id = str(record.get("id", "")).strip()
        if not record_id:
            errors.append(f"{label}[{index}] has no stable id")
        elif record_id in ids:
            errors.append(f"Duplicate {label} id: {record_id}")
        ids.add(record_id)
    return ids


def main() -> int:
    configure_console()
    args = parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    referenced_files: set[Path] = set()

    if not root.is_dir():
        raise SystemExit(f"Wallpaper project does not exist: {root}")

    required = [
        "index.html", "project.json", "static/js/catalog.js", "static/js/app.js",
        "static/css/styles.css", "SOURCES.md", "LICENSE.txt", "NOTICE.txt",
    ]
    for relative in required:
        if not (root / relative).is_file():
            errors.append(f"Missing required file: {relative}")

    text_files = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".html", ".js", ".json", ".md", ".css", ".txt"}:
            try:
                content = path.read_text(encoding="utf-8")
                text_files.append((path, content))
                if PLACEHOLDER.search(content):
                    errors.append(f"Unreplaced placeholder in {path.relative_to(root).as_posix()}")
            except UnicodeDecodeError:
                errors.append(f"Project text file is not UTF-8: {path.relative_to(root).as_posix()}")
    all_project_text = "\n".join(content for _, content in text_files)
    runtime_reference_text = "\n".join(
        content
        for path, content in text_files
        if path.relative_to(root).as_posix() in {"index.html", "project.json"}
        or path.relative_to(root).as_posix().startswith("static/")
    )

    license_path = root / "LICENSE.txt"
    if license_path.is_file() and "Apache License" not in license_path.read_text(encoding="utf-8", errors="replace"):
        errors.append("LICENSE.txt is not the bundled Apache-2.0 license")
    notice_path = root / "NOTICE.txt"
    if notice_path.is_file():
        notice = notice_path.read_text(encoding="utf-8", errors="replace")
        if SKILL_AUTHOR not in notice or SKILL_EMAIL not in notice:
            errors.append("NOTICE.txt is missing the Skill creator attribution")

    project_path = root / "project.json"
    if project_path.is_file():
        try:
            project = json.loads(project_path.read_text(encoding="utf-8"))
            entry = safe_project_path(root, project.get("file", "index.html"), "project.json file", errors)
            if entry:
                referenced_files.add(entry[0])
            preview_value = project.get("preview")
            if preview_value:
                preview = safe_project_path(root, preview_value, "project.json preview", errors)
                if preview:
                    referenced_files.add(preview[0])
            elif args.release:
                warnings.append("No preview is declared; choose a Workshop preview before publishing")
            if args.release and not str(project.get("title", "")).strip():
                errors.append("project.json has no wallpaper title")
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"Invalid project.json: {exc}")

    catalog: dict = {}
    catalog_path = root / "static/js/catalog.js"
    if catalog_path.is_file():
        try:
            catalog = load_catalog(catalog_path)
        except (ValueError, json.JSONDecodeError, OSError) as exc:
            errors.append(f"Invalid catalog.js: {exc}")

    credits = catalog.get("credits", {}) if isinstance(catalog.get("credits", {}), dict) else {}
    uses_reference = credits.get("usesOriginalCubeReference", True)
    if not isinstance(uses_reference, bool):
        errors.append("catalog credits.usesOriginalCubeReference must be true or false")
        uses_reference = True
    if args.release and "usesOriginalCubeReference" not in credits:
        errors.append("Release catalog must explicitly set credits.usesOriginalCubeReference")

    index_path = root / "index.html"
    if index_path.is_file():
        index = index_path.read_text(encoding="utf-8")
        for label, needle in (("skill creator name", SKILL_AUTHOR), ("skill creator email", SKILL_EMAIL)):
            if needle not in index:
                errors.append(f"Visible credits are missing {label}")
        if uses_reference and REFERENCE_URL not in index:
            errors.append("The design is marked as reference-derived but the visible OriginalCube link is missing")
        if not uses_reference and REFERENCE_URL in all_project_text:
            errors.append("OriginalCube inspiration remains in project text although the catalog marks the interface as independent")

    albums = list_records(catalog.get("albums", []), "albums", errors)
    tracks = list_records(catalog.get("tracks", []), "tracks", errors)
    materials = list_records(catalog.get("materials", []), "materials", errors)
    album_ids = record_ids(albums, "albums", errors)
    track_ids = record_ids(tracks, "tracks", errors)
    material_ids = record_ids(materials, "materials", errors)
    del track_ids

    for index, album in enumerate(albums):
        cover_value = album.get("cover")
        if cover_value:
            result = safe_project_path(root, cover_value, f"albums[{index}].cover", errors)
            if result:
                referenced_files.add(result[0])
        if args.release and not str(album.get("title", "")).strip():
            errors.append(f"albums[{index}] has no title")

    audio_paths: defaultdict[str, list[str]] = defaultdict(list)
    for index, track in enumerate(tracks):
        prefix = f"tracks[{index}]"
        track_id = str(track.get("id", "")).strip() or prefix
        for field in ("title", "artist", "audio"):
            if not str(track.get(field, "")).strip():
                errors.append(f"{prefix} has no {field}")
        album_id = str(track.get("albumId", "")).strip()
        if album_id and album_id not in album_ids:
            errors.append(f"{prefix}.albumId does not match an album: {album_id}")
        source_id = str(track.get("sourceId", "")).strip()
        if source_id and source_id not in material_ids:
            errors.append(f"{prefix}.sourceId does not match a material record: {source_id}")
        elif args.release and not source_id:
            warnings.append(f"{prefix} has no sourceId for visible attribution")
        for field in ("audio", "lyrics", "cover", "trackCover"):
            value = track.get(field)
            if not value:
                continue
            result = safe_project_path(root, value, f"{prefix}.{field}", errors)
            if result:
                referenced_files.add(result[0])
                if field == "audio":
                    audio_paths[result[1].lower()].append(track_id)

    for path, ids in audio_paths.items():
        if len(ids) > 1:
            message = f"Audio path is used by multiple tracks ({', '.join(ids)}): {path}"
            (errors if args.release else warnings).append(message)

    for index, material in enumerate(materials):
        if args.release:
            for field in ("name", "creator", "source", "license"):
                if not str(material.get(field, "")).strip():
                    warnings.append(f"materials[{index}] has no {field}")

    if args.release:
        if not tracks:
            errors.append("Release catalog contains no tracks")
        for field in ("title", "author"):
            value = str(catalog.get(field, "")).strip()
            if not value:
                errors.append(f"Release catalog has no {field}")
            elif value.lower().startswith("test ") or value.lower() in {"test", "test author", "wallpaper maker"}:
                warnings.append(f"Catalog {field} still looks like test data: {value}")

    if args.release:
        asset_roots = [root / "assets" / name for name in ("audio", "lyrics", "covers", "logos")]
        for asset_root in asset_roots:
            if not asset_root.is_dir():
                continue
            for path in asset_root.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in MEDIA_SUFFIXES:
                    continue
                relative = path.relative_to(root).as_posix()
                if path.resolve() not in referenced_files and relative not in runtime_reference_text:
                    warnings.append(f"Possibly unused release asset: {relative}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"Validation failed with {len(errors)} error(s) and {len(warnings)} warning(s).")
        return 1
    print(f"Validation passed with {len(warnings)} warning(s): {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
