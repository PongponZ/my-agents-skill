"""Package main_prompt.md and its indexed part prompts/reference PNGs.

Python 3.10+, standard library only. Checks structure, not visual fidelity.
"""
import argparse
import posixpath
import re
import struct
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path, PurePosixPath

SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
PART_PROMPT = re.compile(rf"parts/{SLUG}/prompt\.md")
PART_IMAGE = re.compile(rf"parts/{SLUG}/{SLUG}\.png")
LINK = re.compile(r"!?\[[^\]\r\n]*\]\(([^)\r\n]*)\)")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local_bytes(root, relative):
    path = root.joinpath(*PurePosixPath(relative).parts)
    require(path.resolve().is_relative_to(root), f"File escapes project: {relative}")
    require(path.is_file(), f"Missing file: {relative}")
    data = path.read_bytes()
    require(data, f"Empty file: {relative}")
    return data


def markdown(data, label):
    content = data.decode("utf-8-sig")
    require(content.strip(), f"Empty prompt: {label}")
    require(not re.search(r"\{\{[^}]*\}\}|\[TODO\b", content, re.I),
            f"Unresolved template slot in {label}")
    require(not re.search(r"!?\[[^\]\r\n]*\]\s*\[|^\s*\[[^\]\r\n]+\]:|<\s*(?:img|a)\b",
                          content, re.M | re.I),
            f"Use plain inline Markdown links in {label}")
    return content


def link_targets(content, document):
    targets = []
    for match in LINK.finditer(content):
        target = match[1]
        require(re.fullmatch(r"[a-z0-9_./-]+", target) and not target.startswith("/"),
                f"Unsupported link in {document}: {target}")
        relative = posixpath.normpath(posixpath.join(posixpath.dirname(document), target))
        require(relative != ".." and not relative.startswith("../"),
                f"Link escapes project in {document}: {target}")
        targets.append(relative)
    return targets


def png_dimensions(data, label):
    require(data[:8] == b"\x89PNG\r\n\x1a\n", f"{label} is not encoded as PNG")
    offset, dims, idat, ended = 8, None, False, False
    while offset + 12 <= len(data):
        size = struct.unpack_from(">I", data, offset)[0]
        end = offset + 12 + size
        require(end <= len(data), f"Truncated PNG chunk: {label}")
        kind = data[offset + 4:offset + 8]
        body = data[offset + 8:offset + 8 + size]
        crc = struct.unpack_from(">I", data, offset + 8 + size)[0]
        require(zlib.crc32(kind + body) & 0xffffffff == crc, f"PNG checksum mismatch: {label}")
        if kind == b"IHDR":
            require(offset == 8 and size == 13 and dims is None, f"Invalid PNG header: {label}")
            dims = struct.unpack_from(">II", body)
            require(all(dims), f"PNG dimensions must be positive: {label}")
        elif kind == b"IDAT":
            idat = idat or bool(size)
        elif kind == b"IEND":
            require(size == 0, f"Invalid PNG end chunk: {label}")
            ended = True
            offset = end
            break
        offset = end
    require(dims and idat and ended and offset == len(data), f"Incomplete PNG or trailing data: {label}")
    return dims


def validate_project(project, name=None):
    root = Path(project).resolve(strict=True)
    require(root.is_dir(), "Project must be a directory")
    name = root.name if name is None else name
    require(isinstance(name, str) and len(name) <= 64 and re.fullmatch(SLUG, name),
            "Use a lowercase ASCII hyphen slug for the project directory or --name (max 64 characters)")
    # Windows reserves these names even when they have an extension.
    require(name not in {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)),
                         *(f"lpt{i}" for i in range(1, 10))}, "Reserved artifact name")
    payload = {"main_prompt.md": local_bytes(root, "main_prompt.md")}
    main = markdown(payload["main_prompt.md"], "main_prompt.md")
    parts = list(dict.fromkeys(link_targets(main, "main_prompt.md")))
    require(parts, "main_prompt.md must index at least one part prompt")
    require(all(PART_PROMPT.fullmatch(p) for p in parts),
            "Main may link only parts/<part-id>/prompt.md")
    for part in parts:
        payload[part] = local_bytes(root, part)
        content = markdown(payload[part], part)
        for heading in ("Reference", "Build", "Check"):
            sections = list(re.finditer(rf"^## {heading}[ \t]*\r?$", content, re.M))
            require(len(sections) == 1, f"{part} needs one ## {heading} section")
            tail = content[sections[0].end():]
            body = re.split(r"^## ", tail, maxsplit=1, flags=re.M)[0]
            require(body.strip(), f"Empty {heading} section in {part}")
        references = re.split(r"^## ", re.split(r"^## Reference[ \t]*\r?$", content,
                              maxsplit=1, flags=re.M)[1], maxsplit=1, flags=re.M)[0]
        reference_targets = link_targets(references, part)
        images = set()
        for target in link_targets(content, part):
            if target == "main_prompt.md" or target in parts:
                continue
            require(PART_IMAGE.fullmatch(target)
                    and PurePosixPath(target).parent == PurePosixPath(part).parent,
                    f"Unsupported target or unindexed dependency in {part}: {target}")
            if target not in payload:
                payload[target] = local_bytes(root, target)
                png_dimensions(payload[target], target)
            images.add(target)
        require(images.intersection(reference_targets),
                f"{part} needs a local PNG link in its Reference section")
    return name, payload


def package(project, output_dir, name=None):
    name, payload = validate_project(project, name)
    destination_dir = Path(output_dir).resolve()
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"{name}_artifact.zip"
    require(not destination.exists(), f"Archive already exists; choose another output directory: {destination}")
    # Freeze validated bytes, verify the complete archive, then publish exclusively.
    with tempfile.TemporaryDirectory(prefix="modeling-package-") as temporary:
        staged = Path(temporary) / "artifact.zip"
        with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for relative, data in sorted(payload.items()):
                archive.writestr(f"{name}/{relative}", data)
        with zipfile.ZipFile(staged) as archive:
            require(archive.testzip() is None, "ZIP integrity validation failed")
            require(len(archive.namelist()) == len(payload), "Unexpected ZIP contents")
            for relative, data in payload.items():
                require(archive.read(f"{name}/{relative}") == data, "Archive byte mismatch")
        created = False
        try:
            with destination.open("xb") as target:
                created = True
                target.write(staged.read_bytes())
        except BaseException:
            if created:
                destination.unlink(missing_ok=True)
            raise
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--name", help="Artifact slug; defaults to project directory name")
    args = parser.parse_args()
    try:
        output = package(args.project, args.output_dir, args.name)
    except (OSError, ValueError, struct.error, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
