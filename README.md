# PDF and DOCX Metadata Remover

A Python command-line utility to remove common document metadata from PDF and Microsoft Word (`.docx`) files. It supports processing individual files or entire directories, with optional recursive scanning of subdirectories.

The script creates cleaned copies in a separate output directory, leaving the original files unchanged.

## Features

- **PDF metadata removal:** Clears standard document information fields, including Title, Author, Subject, Keywords, Creator, and Producer.
- **PDF catalog cleanup:** Removes common catalog metadata entries such as `/Metadata` and `/PieceInfo` when present.
- **DOCX metadata removal:** Removes standard core, extended, and custom document property files.
- **Batch processing:** Processes multiple PDF and DOCX files from a directory.
- **Recursive scanning:** Optionally searches subdirectories for supported files.
- **Separate output directory:** Saves processed files separately to avoid modifying originals.
- **Error handling:** Reports unsupported file types and processing errors.
- **Cross-platform compatibility:** Works on Windows, Linux, and macOS with Python installed.

## Requirements

- Python 3.9 or later recommended
- `pypdf`

> Note: `python-docx` is listed in the original script's installation instructions, but the current implementation does not use it.

## Installation

### 1. Install Python

Download Python from the official website: https://www.python.org/downloads/

Verify the installation:

```bash
python --version
```

### 2. Install the dependency

```bash
python -m pip install pypdf
```

### 3. Save the script

Save the Python code as:

```text
remove_metadata.py
```

## Usage

Run the script from your terminal or command prompt.

### Process a single PDF file

```bash
python remove_metadata.py "report.pdf"
```

### Process a single DOCX file

```bash
python remove_metadata.py "report.docx"
```

### Process files in a directory

```bash
python remove_metadata.py "C:\Docs"
```

By default, only files directly inside the specified directory are processed.

### Process files recursively

Use `--recursive` or `-r` to include subdirectories:

```bash
python remove_metadata.py "C:\Docs" --recursive
```

Short form:

```bash
python remove_metadata.py "C:\Docs" -r
```

### Specify a custom output directory

Use `--output` or `-o`:

```bash
python remove_metadata.py "C:\Docs" --output "C:\CleanedFiles"
```

Recursive processing with a custom output directory:

```bash
python remove_metadata.py "C:\Docs" -r -o "C:\CleanedFiles"
```

Linux/macOS example:

```bash
python remove_metadata.py "/home/user/Documents" --recursive
```

## Output

By default, the script creates a directory named `metadata_removed`.

- For a single file, the directory is created alongside the input file.
- For a directory input, the directory is created inside the specified directory.

Example:

```text
C:\Docs\
├── report.pdf
├── proposal.docx
└── metadata_removed\
    ├── report_metadata_removed.pdf
    └── proposal_metadata_removed.docx
```

Output files use this naming pattern:

```text
original_filename_metadata_removed.extension
```

Example:

```text
report.pdf
    ↓
report_metadata_removed.pdf
```

The script prints a status message for each file. Example output:

```text
[OK]   report.pdf -> metadata_removed/report_metadata_removed.pdf
[SKIP] Unsupported file type: image.png
[ERROR] report.pdf: Error details

Finished: 2 of 3 file(s) processed.
```

The output above is illustrative; actual messages depend on the files processed.

## Metadata Covered

### PDF files

The script clears these standard document-information fields:

| Metadata field | Description |
|---|---|
| `/Title` | Document title |
| `/Author` | Document author |
| `/Subject` | Document subject |
| `/Keywords` | Document keywords |
| `/Creator` | Application that created the document |
| `/Producer` | Software that generated the PDF |

It also removes `/Metadata` and `/PieceInfo` entries from the PDF catalog when present.

### DOCX files

The script removes these standard metadata parts:

| File | Description |
|---|---|
| `docProps/core.xml` | Core properties, such as author, title, and creation date |
| `docProps/app.xml` | Extended application properties |
| `docProps/custom.xml` | Custom document properties |

It also updates package content-type declarations and relationships associated with these parts.

## Limitations

This utility removes common metadata; it does **not** guarantee complete or forensic-grade sanitization.

- PDF metadata may also exist in XMP streams, annotations, attachments, embedded files, form fields, comments, or other structures not covered by the script.
- DOCX files may contain identifying information in comments, tracked changes, headers, footers, embedded objects, images, and document content.
- Rewriting a PDF can affect features such as digital signatures, forms, bookmarks, or other complex structures, depending on the source file.
- PDF metadata fields are set to empty strings rather than necessarily being removed entirely.
- Only `.pdf` and `.docx` files are supported. Formats such as `.doc`, `.docm`, `.xlsx`, `.pptx`, and image files are not processed.
- Removing metadata does not anonymize visible text or guarantee that the author cannot be identified.

For sensitive documents, independently inspect the output with suitable metadata-analysis tools before sharing it.

## Exit Codes

| Exit code | Meaning |
|---|---|
| `0` | Processing completed successfully |
| `1` | Processing failed, no supported files were found, or one or more files could not be processed |

## Security and Privacy

- Original files are not intentionally modified.
- Output files may still contain residual metadata or identifying information.
- Keep backups of important documents before processing.
- Verify cleaned files before publishing or sharing sensitive information.
- Use the utility only on files you own or are authorized to process.

## License

Add an appropriate license before distributing this project publicly. Without a license, users should not assume that the project is released under an open-source license.

## Disclaimer

This tool is provided for document metadata cleanup and privacy-related workflows. It is not a substitute for comprehensive document sanitization. Successful execution does not prove that all metadata or identifying information has been removed.
