#!/usr/bin/env python3
"""
Remove common metadata from PDF and DOCX files.

Install dependencies:
    python -m pip install pypdf python-docx

Examples:
    python remove_metadata.py "report.pdf"
    python remove_metadata.py "report.docx"
    python remove_metadata.py "C:\\Docs" --recursive

Cleaned files are written to a new output folder; originals are not changed.
"""

import argparse
import sys
import zipfile
from pathlib import Path
from tempfile import NamedTemporaryFile
from xml.etree import ElementTree as ET

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def clean_pdf(source: Path, destination: Path) -> None:
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency. Install it with: python -m pip install pypdf"
        ) from exc

    reader = PdfReader(str(source))
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    # Clear standard PDF document-information metadata.
    writer.add_metadata({
        "/Title": "",
        "/Author": "",
        "/Subject": "",
        "/Keywords": "",
        "/Creator": "",
        "/Producer": "",
    })

    # pypdf can copy document-level structures when cloning. Remove common
    # catalog metadata entries from the writer's root object where present.
    root = writer._root_object
    for key in ("/Metadata", "/PieceInfo"):
        if key in root:
            del root[key]

    with destination.open("wb") as output:
        writer.write(output)


def clean_docx(source: Path, destination: Path) -> None:
    # DOCX is a ZIP package. Remove standard core, extended, and custom
    # property parts, then remove their references from [Content_Types].xml
    # and package relationships. Document content is otherwise preserved.
    content_types_ns = "http://schemas.openxmlformats.org/package/2006/content-types"
    rels_ns = "http://schemas.openxmlformats.org/package/2006/relationships"

    property_parts = {
        "docProps/core.xml",
        "docProps/app.xml",
        "docProps/custom.xml",
    }
    property_content_types = {
        "application/vnd.openxmlformats-package.core-properties+xml",
        "application/vnd.openxmlformats-officedocument.extended-properties+xml",
        "application/vnd.openxmlformats-officedocument.custom-properties+xml",
    }
    property_rel_types = {
        "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties",
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties",
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/custom-properties",
    }

    with zipfile.ZipFile(source, "r") as zin:
        entries = {info.filename: (info, zin.read(info.filename)) for info in zin.infolist()}

    # Update [Content_Types].xml.
    if "[Content_Types].xml" in entries:
        info, data = entries["[Content_Types].xml"]
        root = ET.fromstring(data)
        for child in list(root):
            part_name = child.attrib.get("PartName", "").lstrip("/")
            content_type = child.attrib.get("ContentType", "")
            if part_name in property_parts or content_type in property_content_types:
                root.remove(child)
        entries["[Content_Types].xml"] = (
            info,
            ET.tostring(root, encoding="utf-8", xml_declaration=True),
        )

    # Update package-level relationships.
    rels_name = "_rels/.rels"
    if rels_name in entries:
        info, data = entries[rels_name]
        root = ET.fromstring(data)
        for child in list(root):
            rel_type = child.attrib.get("Type", "")
            target = child.attrib.get("Target", "").lstrip("/")
            if rel_type in property_rel_types or target in property_parts:
                root.remove(child)
        entries[rels_name] = (
            info,
            ET.tostring(root, encoding="utf-8", xml_declaration=True),
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, (info, data) in entries.items():
            if name in property_parts:
                continue
            # Avoid preserving original per-entry compression settings that
            # could be inconsistent after rewriting.
            zout.writestr(name, data)


def output_path(source: Path, output_dir: Path) -> Path:
    return output_dir / f"{source.stem}_metadata_removed{source.suffix}"


def process_file(source: Path, output_dir: Path) -> bool:
    if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
        print(f"[SKIP] Unsupported file type: {source}")
        return False

    destination = output_path(source, output_dir)
    if source.resolve() == destination.resolve():
        print(f"[SKIP] Output would overwrite source: {source}")
        return False

    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix.lower() == ".pdf":
            clean_pdf(source, destination)
        else:
            clean_docx(source, destination)
        print(f"[OK]   {source} -> {destination}")
        return True
    except Exception as exc:
        print(f"[ERROR] {source}: {exc}", file=sys.stderr)
        if destination.exists():
            try:
                destination.unlink()
            except OSError:
                pass
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove common metadata from PDF and DOCX files."
    )
    parser.add_argument("path", help="Input PDF/DOCX file or folder")
    parser.add_argument(
        "-o", "--output",
        help="Output folder (default: metadata_removed next to input)",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="When input is a folder, scan subfolders recursively",
    )
    args = parser.parse_args()

    source = Path(args.path).expanduser().resolve()
    if not source.exists():
        parser.error(f"Input does not exist: {source}")

    if args.output:
        output_dir = Path(args.output).expanduser().resolve()
    elif source.is_dir():
        output_dir = source / "metadata_removed"
    else:
        output_dir = source.parent / "metadata_removed"

    if source.is_file():
        success = process_file(source, output_dir)
        return 0 if success else 1

    iterator = source.rglob("*") if args.recursive else source.iterdir()
    files = [
        p for p in iterator
        if p.is_file()
        and p.suffix.lower() in SUPPORTED_EXTENSIONS
        and output_dir not in p.parents
    ]
    if not files:
        print("No PDF or DOCX files found.")
        return 1

    results = [process_file(p, output_dir) for p in files]
    print(f"\nFinished: {sum(results)} of {len(results)} file(s) processed.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
