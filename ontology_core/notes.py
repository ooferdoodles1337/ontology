"""Course-note section loading for the local web reader."""

from __future__ import annotations

import json
import re
from pathlib import Path

from pypdf import PdfReader

from .knowledge_base import load_documents
from .paths import DEFAULT_MANIFEST_DIR, ROOT


def extract_pdf_lines(pdf_path: Path) -> list[str]:
    """Return non-empty normalized PDF lines aligned with RAG manifests."""
    reader = PdfReader(str(pdf_path))
    lines: list[str] = []
    for page_index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text(extraction_mode="layout") or ""
        except TypeError:
            text = page.extract_text() or ""
        for raw_line in text.splitlines():
            line = re.sub(r"\s+", " ", raw_line).strip()
            if not line or line == str(page_index):
                continue
            lines.append(line)
    return lines


def load_doc_sections(doc_id: str) -> dict | None:
    manifest_path = DEFAULT_MANIFEST_DIR / f"{doc_id}.sections.json"
    if not manifest_path.exists():
        return None

    with manifest_path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)

    doc = next((item for item in load_documents() if item["id"] == doc_id), None)
    if not doc:
        return None

    pdf_path = ROOT / doc["source_path"]
    if not pdf_path.exists():
        return None

    all_lines = extract_pdf_lines(pdf_path)
    sections = []
    for section in manifest["sections"]:
        chunk = all_lines[section["line_start"]:section["line_end"]]
        sections.append(
            {
                "section_id": section["section_id"],
                "title": section["title"],
                "level": section["level"],
                "page_start": section["page_start"],
                "text": "\n".join(chunk),
            }
        )

    return {"doc_id": doc_id, "title": doc["title"], "sections": sections}

