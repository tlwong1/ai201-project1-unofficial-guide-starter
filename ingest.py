"""
ingest.py
Loads documents from the documents/ folder, extracts text, cleans it,
and saves structured JSON output to documents/processed/.
Handles: .pdf (via pdfplumber), .txt (direct read)
Skips: .htm, .html, .gitkeep, and anything else
"""

import os
import json
import re
import pdfplumber
from bs4 import BeautifulSoup
from pathlib import Path

DOCUMENTS_DIR = Path("documents")
OUTPUT_DIR = Path("documents/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_pdf(filepath: Path) -> str:
    """Extract text from a PDF using pdfplumber."""
    pages = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n\n".join(pages)


def extract_txt(filepath: Path) -> str:
    """Read a plain text file."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def clean_text(text: str) -> str:
    """
    Remove navigation noise, HTML artifacts, and boilerplate.
    Keeps substantive content only.
    """
    # Strip any residual HTML tags
    text = BeautifulSoup(text, "html.parser").get_text(separator="\n")

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # Remove lines that are clearly navigation / boilerplate
    nav_patterns = [
        r'^\s*skip to',
        r'^\s*toggle',
        r'^\s*show sub menu',
        r'^\s*close menu',
        r'^\s*search$',
        r'^\s*menu$',
        r'^\s*home\s*$',
        r'^\s*print options',
        r'^\s*download page',
        r'^\s*back to top',
        r'^\s*©\s*\d{4}',
        r'^\s*all rights reserved',
        r'^\s*privacy statement',
        r'^\s*terms of use',
        r'^\s*accessibility',
        r'^\s*follow us on',
        r'^\s*subscribe',
        r'^\s*give\s*$',
        r'^\s*apply\s*$',
        r'^\s*connect\s*$',
    ]

    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if any(re.match(p, stripped, re.IGNORECASE) for p in nav_patterns):
            continue
        cleaned_lines.append(stripped)

    # Collapse multiple blank lines
    text = "\n".join(cleaned_lines)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def process_documents():
    results = []
    skipped = []

    for filepath in sorted(DOCUMENTS_DIR.iterdir()):
        # Skip subdirectories and non-target files
        if filepath.is_dir():
            continue
        if filepath.suffix.lower() in (".htm", ".html", ".gitkeep", ""):
            skipped.append(filepath.name)
            continue
        if filepath.name == ".gitkeep":
            continue

        suffix = filepath.suffix.lower()

        if suffix == ".pdf":
            print(f"[PDF] {filepath.name}")
            raw_text = extract_pdf(filepath)
        elif suffix == ".txt":
            print(f"[TXT] {filepath.name}")
            raw_text = extract_txt(filepath)
        else:
            print(f"[SKIP] {filepath.name}")
            skipped.append(filepath.name)
            continue

        if not raw_text.strip():
            print(f"  WARNING: no text extracted from {filepath.name}")
            continue

        cleaned = clean_text(raw_text)
        word_count = len(cleaned.split())

        doc = {
            "source": filepath.name,
            "text": cleaned,
            "word_count": word_count,
        }

        # Save individual JSON file
        out_path = OUTPUT_DIR / (filepath.stem + ".json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

        print(f"  -> {word_count} words saved to {out_path.name}")
        results.append({"source": filepath.name, "word_count": word_count})

    print(f"\nDone. Processed {len(results)} documents, skipped {len(skipped)}.")
    for r in results:
        print(f"  {r['source']}: {r['word_count']} words")

    if skipped:
        print(f"\nSkipped: {skipped}")


if __name__ == "__main__":
    process_documents()