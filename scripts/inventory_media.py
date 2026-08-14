#!/usr/bin/env python3
"""Inventory wallpaper media and report quality signals without changing originals."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import wave
from collections import Counter, defaultdict
from pathlib import Path


CATEGORIES = {
    "audio": {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".opus", ".aac"},
    "lyrics": {".lrc", ".txt", ".srt", ".vtt"},
    "image": {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".bmp", ".avif"},
    "font": {".ttf", ".otf", ".woff", ".woff2"},
}
LRC_TIMESTAMP = re.compile(r"\[(?:(\d{1,2}):)?\d{1,3}:\d{1,2}(?:[.:]\d{1,3})?\]")
LRC_TAG = re.compile(r"^\[([A-Za-z][A-Za-z0-9_-]*):(.*)\]$")

try:
    import mutagen  # type: ignore
except ImportError:
    mutagen = None


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Material directory to inspect")
    parser.add_argument("--output", type=Path, required=True, help="JSON report path")
    parser.add_argument("--hash", action="store_true", help="Include SHA-256 hashes and duplicate groups")
    parser.add_argument("--min-image-side", type=int, default=1000, help="Warn when a raster image's shorter side is below this value")
    return parser.parse_args()


def category_for(path: Path) -> str | None:
    suffix = path.suffix.lower()
    return next((name for name, extensions in CATEGORIES.items() if suffix in extensions), None)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def jpeg_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as stream:
        if stream.read(2) != b"\xff\xd8":
            return None
        while True:
            byte = stream.read(1)
            if not byte:
                return None
            if byte != b"\xff":
                continue
            marker = stream.read(1)
            while marker == b"\xff":
                marker = stream.read(1)
            if not marker:
                return None
            if marker in {bytes([value]) for value in range(0xC0, 0xC4)} | {bytes([value]) for value in range(0xC5, 0xC8)} | {bytes([value]) for value in range(0xC9, 0xCC)} | {bytes([value]) for value in range(0xCD, 0xD0)}:
                length = stream.read(2)
                precision_and_size = stream.read(5)
                if len(length) != 2 or len(precision_and_size) != 5:
                    return None
                height, width = struct.unpack(">HH", precision_and_size[1:5])
                return width, height
            if marker in {b"\xd8", b"\xd9"} or 0xD0 <= marker[0] <= 0xD7:
                continue
            length_bytes = stream.read(2)
            if len(length_bytes) != 2:
                return None
            length = struct.unpack(">H", length_bytes)[0]
            stream.seek(max(0, length - 2), 1)


def svg_size(path: Path) -> tuple[float, float] | None:
    with path.open("r", encoding="utf-8", errors="replace") as stream:
        text = stream.read(65536)
    view_box = re.search(r"\bviewBox\s*=\s*['\"]\s*[-+\d.eE]+[ ,]+[-+\d.eE]+[ ,]+([-+\d.eE]+)[ ,]+([-+\d.eE]+)", text)
    if view_box:
        return float(view_box.group(1)), float(view_box.group(2))
    width = re.search(r"\bwidth\s*=\s*['\"]([\d.]+)(?:px)?['\"]", text)
    height = re.search(r"\bheight\s*=\s*['\"]([\d.]+)(?:px)?['\"]", text)
    if width and height:
        return float(width.group(1)), float(height.group(1))
    return None


def image_size(path: Path) -> tuple[float, float, bool] | None:
    suffix = path.suffix.lower()
    if suffix == ".svg":
        size = svg_size(path)
        return (*size, True) if size else None
    with path.open("rb") as stream:
        header = stream.read(64)
    if suffix == ".png" and header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
        width, height = struct.unpack(">II", header[16:24])
        return width, height, False
    if suffix == ".gif" and header[:6] in {b"GIF87a", b"GIF89a"} and len(header) >= 10:
        width, height = struct.unpack("<HH", header[6:10])
        return width, height, False
    if suffix == ".bmp" and header.startswith(b"BM") and len(header) >= 26:
        width, height = struct.unpack("<ii", header[18:26])
        return abs(width), abs(height), False
    if suffix in {".jpg", ".jpeg"}:
        size = jpeg_size(path)
        return (*size, False) if size else None
    if suffix == ".webp" and header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        if header[12:16] == b"VP8X" and len(header) >= 30:
            width = 1 + int.from_bytes(header[24:27], "little")
            height = 1 + int.from_bytes(header[27:30], "little")
            return width, height, False
        if header[12:16] == b"VP8L" and len(header) >= 25 and header[20] == 0x2F:
            bits = int.from_bytes(header[21:25], "little")
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1, False
    return None


def inspect_image(path: Path, min_side: int) -> tuple[dict, list[str]]:
    warnings: list[str] = []
    size = image_size(path)
    if not size:
        return {"dimensionsAvailable": False}, ["image-dimensions-unavailable"]
    width, height, is_vector = size
    details = {
        "dimensionsAvailable": True,
        "width": round(width, 2),
        "height": round(height, 2),
        "aspectRatio": round(width / height, 4) if height else None,
        "isVector": is_vector,
    }
    if not is_vector and min(width, height) < min_side:
        warnings.append(f"raster-short-side-below-{min_side}px")
    return details, warnings


def decode_lyrics(data: bytes) -> tuple[str | None, str, list[str]]:
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig"), "utf-8-sig", []
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16"), "utf-16", ["lyrics-not-utf8"]
    if len(data) >= 4 and len(data) % 2 == 0 and data[1::2].count(0) > len(data) // 4:
        return data.decode("utf-16-le"), "utf-16-le", ["lyrics-not-utf8"]
    if len(data) >= 4 and len(data) % 2 == 0 and data[0::2].count(0) > len(data) // 4:
        return data.decode("utf-16-be"), "utf-16-be", ["lyrics-not-utf8"]
    try:
        return data.decode("utf-8"), "utf-8", []
    except UnicodeDecodeError:
        candidates = []
        for encoding in ("gb18030", "shift_jis"):
            try:
                data.decode(encoding)
                candidates.append(encoding)
            except UnicodeDecodeError:
                pass
        if len(candidates) == 1:
            return data.decode(candidates[0]), candidates[0], ["lyrics-not-utf8"]
        if candidates:
            return None, "undetermined", ["lyrics-encoding-ambiguous", *[f"encoding-candidate-{item}" for item in candidates]]
        return None, "unknown", ["lyrics-cannot-be-decoded"]


def inspect_lyrics(path: Path) -> tuple[dict, list[str]]:
    text, encoding, warnings = decode_lyrics(path.read_bytes())
    details: dict = {"encoding": encoding, "timestampCount": 0, "metadata": {}}
    if text is None:
        return details, warnings
    details["timestampCount"] = len(LRC_TIMESTAMP.findall(text))
    metadata = {}
    for line in text.splitlines():
        match = LRC_TAG.match(line.strip())
        if match and match.group(1).lower() in {"ti", "ar", "al", "by", "offset", "re", "ve"}:
            metadata[match.group(1).lower()] = match.group(2).strip()
    details["metadata"] = metadata
    if path.suffix.lower() == ".lrc" and not details["timestampCount"]:
        warnings.append("lrc-has-no-valid-timestamps")
    return details, warnings


def inspect_audio(path: Path) -> tuple[dict, list[str]]:
    details: dict = {"metadataAvailable": False}
    warnings: list[str] = []
    if path.suffix.lower() == ".wav":
        try:
            with wave.open(str(path), "rb") as audio:
                rate = audio.getframerate()
                details.update({
                    "metadataAvailable": True,
                    "durationSeconds": round(audio.getnframes() / rate, 3) if rate else None,
                    "sampleRate": rate,
                    "channels": audio.getnchannels(),
                    "bitsPerSample": audio.getsampwidth() * 8,
                })
                return details, warnings
        except (wave.Error, OSError):
            warnings.append("wav-metadata-invalid")
    if mutagen is not None:
        try:
            media = mutagen.File(path, easy=True)
            if media is not None:
                info = getattr(media, "info", None)
                tags = getattr(media, "tags", {}) or {}
                details.update({
                    "metadataAvailable": True,
                    "durationSeconds": round(float(getattr(info, "length", 0)), 3) or None,
                    "bitrate": getattr(info, "bitrate", None),
                    "sampleRate": getattr(info, "sample_rate", None),
                    "channels": getattr(info, "channels", None),
                    "tags": {key: list(value) if isinstance(value, (list, tuple)) else str(value) for key, value in tags.items() if key in {"title", "artist", "album", "tracknumber"}},
                })
                return details, warnings
        except Exception as exc:
            warnings.append(f"audio-metadata-read-failed-{type(exc).__name__}")
    warnings.append("audio-metadata-not-inspected")
    return details, warnings


def main() -> int:
    configure_console()
    args = parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    if not root.is_dir():
        raise SystemExit(f"Material directory does not exist: {root}")
    if args.min_image_side < 1:
        raise SystemExit("--min-image-side must be positive")

    files = []
    counts: Counter[str] = Counter()
    bytes_by_category: Counter[str] = Counter()
    warning_counts: Counter[str] = Counter()
    hashes: defaultdict[str, list[str]] = defaultdict(list)
    candidates = sorted((item for item in root.rglob("*") if item.is_file()), key=lambda item: item.as_posix().lower())
    for path in candidates:
        category = category_for(path)
        if category is None or path.resolve() == output:
            continue
        size = path.stat().st_size
        entry: dict = {
            "relativePath": path.relative_to(root).as_posix(),
            "category": category,
            "extension": path.suffix.lower(),
            "sizeBytes": size,
        }
        warnings: list[str] = []
        if category == "image":
            entry["quality"], warnings = inspect_image(path, args.min_image_side)
        elif category == "lyrics":
            entry["quality"], warnings = inspect_lyrics(path)
        elif category == "audio":
            entry["quality"], warnings = inspect_audio(path)
        if warnings:
            entry["warnings"] = warnings
            warning_counts.update(warnings)
        if args.hash:
            digest = sha256(path)
            entry["sha256"] = digest
            hashes[digest].append(entry["relativePath"])
        files.append(entry)
        counts[category] += 1
        bytes_by_category[category] += size

    duplicate_groups = [paths for paths in hashes.values() if len(paths) > 1]
    report = {
        "root": str(root),
        "capabilities": {"mutagenAudioMetadata": mutagen is not None},
        "summary": {
            "fileCount": len(files),
            "totalBytes": sum(item["sizeBytes"] for item in files),
            "counts": dict(sorted(counts.items())),
            "bytesByCategory": dict(sorted(bytes_by_category.items())),
            "warningCounts": dict(sorted(warning_counts.items())),
            "duplicateGroupCount": len(duplicate_groups),
        },
        "duplicateGroups": duplicate_groups,
        "files": files,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Inventoried {len(files)} files with {sum(warning_counts.values())} quality warning(s) -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
