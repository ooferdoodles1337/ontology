#!/usr/bin/env python3
"""Local RAG retrieval over FAB course notes and ontology records."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import logging
import os
import re
import sqlite3
import subprocess
import sys
import warnings
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pypdf import PdfReader

try:
    from .config import (
        COURSE_NOTES_DIR,
        DB_PATH,
        DEFAULT_CHROMA_DIR,
        DEFAULT_MANIFEST_DIR,
        DEFAULT_RAG_DIR,
        DEFAULT_REVIEW_DIR,
        DOCUMENTS_YAML,
        NODES_YAML,
        RELATIONS_YAML,
        ROOT,
    )
except ImportError:
    from config import (
        COURSE_NOTES_DIR,
        DB_PATH,
        DEFAULT_CHROMA_DIR,
        DEFAULT_MANIFEST_DIR,
        DEFAULT_RAG_DIR,
        DEFAULT_REVIEW_DIR,
        DOCUMENTS_YAML,
        NODES_YAML,
        RELATIONS_YAML,
        ROOT,
    )

DEFAULT_COLLECTION = "fab_ontology"
DEFAULT_EMBED_MODEL = os.environ.get(
    "ONTOLOGY_RAG_EMBED_MODEL", "jinaai/jina-embeddings-v5-text-nano"
)
DEFAULT_MAX_LENGTH = int(os.environ.get("ONTOLOGY_RAG_MAX_LENGTH", "8192"))

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")

NODE_GROUPS = [
    ("concepts", "concept"),
    ("people_and_institutions", "person_or_institution"),
    ("examples_and_metaphors", "example"),
]

logging.getLogger("pypdf").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=FutureWarning, module=r"transformers\..*")


@dataclass(frozen=True)
class ExtractedLine:
    index: int
    page: int
    page_line: int
    text: str


@dataclass(frozen=True)
class PdfSection:
    section_id: str
    title: str
    level: int
    page_start: int
    page_end: int
    line_start: int
    line_end: int
    word_count: int
    text: str


def normalize_space(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def slugify(value: str) -> str:
    value = normalize_space(value).lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "document"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT))


def display_path(path: Path | str) -> str:
    resolved = Path(path).resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open() as handle:
        return yaml.safe_load(handle) or {}


@contextlib.contextmanager
def quiet_external_output(enabled: bool = True):
    if not enabled or os.environ.get("ONTOLOGY_RAG_VERBOSE"):
        yield
        return
    with open(os.devnull, "w") as devnull:
        with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
            yield


def normalize_document_text(value: Any) -> str:
    value = normalize_space(value).lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return normalize_space(value)


@lru_cache(maxsize=1)
def load_document_records() -> list[dict[str, Any]]:
    if not DOCUMENTS_YAML.exists():
        return []
    data = load_yaml(DOCUMENTS_YAML)
    return [
        entry
        for entry in data.get("documents", []) or []
        if normalize_space(entry.get("id"))
    ]


def infer_doc_id(path: Path) -> str:
    path = path.resolve()
    try:
        relative_path = relpath(path)
    except ValueError:
        relative_path = str(path)

    haystack = normalize_document_text(path.stem)
    best_match: tuple[int, str] | None = None
    for record in load_document_records():
        doc_id = normalize_space(record.get("id"))
        source_path = normalize_space(record.get("source_path"))
        if source_path:
            source_name = Path(source_path).name
            if source_path == relative_path or source_name == path.name:
                return doc_id

        terms = [record.get("title"), *(record.get("aliases") or [])]
        for term in terms:
            normalized_term = normalize_document_text(term)
            if normalized_term and normalized_term in haystack:
                score = len(normalized_term)
                if best_match is None or score > best_match[0]:
                    best_match = (score, doc_id)

    if best_match:
        return best_match[1]
    return f"notes_{slugify(path.stem)}"


def document_record_for(path: Path) -> dict[str, Any] | None:
    doc_id = infer_doc_id(path)
    for record in load_document_records():
        if record.get("id") == doc_id:
            return record
    return None


def course_note_sort_key(path: Path) -> tuple[int, str]:
    record = document_record_for(path) or {}
    try:
        course_order = int(record.get("course_order"))
    except (TypeError, ValueError):
        course_order = 10_000
    return course_order, pdf_title(path)


def course_note_paths() -> list[Path]:
    return sorted(COURSE_NOTES_DIR.glob("*.pdf"), key=course_note_sort_key)


def pdf_title(path: Path) -> str:
    record = document_record_for(path)
    if record:
        title = normalize_space(record.get("title"))
        if title:
            return title
    title = normalize_space(path.stem.replace("_", " "))
    title = re.sub(r"\bCourse Notes\b", "Course Notes", title)
    return title


def extract_pdf_lines(path: Path) -> list[ExtractedLine]:
    reader = PdfReader(str(path))
    lines: list[ExtractedLine] = []
    global_index = 0
    for page_index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text(extraction_mode="layout") or ""
        except TypeError:
            text = page.extract_text() or ""
        for page_line, raw_line in enumerate(text.splitlines()):
            line = normalize_space(raw_line)
            if not line:
                continue
            if line == str(page_index):
                continue
            lines.append(
                ExtractedLine(
                    index=global_index,
                    page=page_index,
                    page_line=page_line,
                    text=line,
                )
            )
            global_index += 1
    return lines


def parse_numbered_heading(line: str) -> tuple[str, str, int] | None:
    match = re.match(r"^(?P<num>\d+(?:\.\d+)*)(?P<trailing_dot>\.)?\s+(?P<title>.+)$", line)
    if not match:
        return None

    number = match.group("num")
    title = normalize_space(match.group("title"))
    if not title or title[0].islower() or title[0].isdigit():
        return None
    if len(title) > 110:
        return None
    if title.lower().startswith(("cf.", "or ", "and ", "by ", "of ")):
        return None

    has_hierarchy = "." in number
    has_trailing_dot = bool(match.group("trailing_dot"))
    no_dot_allowed = (
        not has_hierarchy
        and not has_trailing_dot
        and number.isdigit()
        and int(number) <= 9
        and len(title) <= 60
    )
    if not has_hierarchy and not has_trailing_dot and not no_dot_allowed:
        return None

    level = number.count(".") + 1
    return number, title, level


def section_text(lines: list[ExtractedLine], start: int, end: int) -> str:
    selected = lines[start:end]
    text = "\n".join(line.text for line in selected)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build_section(
    lines: list[ExtractedLine],
    doc_slug: str,
    ordinal: int,
    title: str,
    level: int,
    start: int,
    end: int,
) -> PdfSection | None:
    if start >= end:
        return None
    text = section_text(lines, start, end)
    word_count = len(text.split())
    if word_count < 20:
        return None
    selected = lines[start:end]
    return PdfSection(
        section_id=f"{doc_slug}:{ordinal:03d}",
        title=title,
        level=level,
        page_start=selected[0].page,
        page_end=selected[-1].page,
        line_start=start,
        line_end=end,
        word_count=word_count,
        text=text,
    )


def draft_pdf_sections(path: Path) -> list[PdfSection]:
    lines = extract_pdf_lines(path)
    if not lines:
        return []

    doc_slug = slugify(path.stem)
    headings: list[tuple[int, str, int]] = []
    for line in lines:
        parsed = parse_numbered_heading(line.text)
        if parsed:
            _, title, level = parsed
            headings.append((line.index, title, level))

    if not headings:
        whole_doc = build_section(
            lines, doc_slug, 1, pdf_title(path), 1, 0, len(lines)
        )
        return [whole_doc] if whole_doc else []

    sections: list[PdfSection] = []
    first_heading_start = headings[0][0]
    ordinal = 1

    if len(section_text(lines, 0, first_heading_start).split()) >= 80:
        front_matter = build_section(
            lines, doc_slug, ordinal, "Front Matter", 1, 0, first_heading_start
        )
        if front_matter:
            sections.append(front_matter)
            ordinal += 1
    else:
        first_heading_start = 0

    for heading_index, (start, title, level) in enumerate(headings):
        if heading_index == 0:
            start = first_heading_start
        end = headings[heading_index + 1][0] if heading_index + 1 < len(headings) else len(lines)
        section = build_section(lines, doc_slug, ordinal, title, level, start, end)
        if section:
            sections.append(section)
            ordinal += 1

    return sections


def manifest_path_for(pdf_path: Path, manifest_dir: Path) -> Path:
    return manifest_dir / f"{infer_doc_id(pdf_path)}.sections.json"


def serialize_section(section: PdfSection) -> dict[str, Any]:
    return {
        "section_id": section.section_id,
        "title": section.title,
        "level": section.level,
        "page_start": section.page_start,
        "page_end": section.page_end,
        "line_start": section.line_start,
        "line_end": section.line_end,
        "word_count": section.word_count,
    }


def write_section_manifest(pdf_path: Path, sections: list[PdfSection], manifest_dir: Path) -> Path:
    manifest_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "doc_id": infer_doc_id(pdf_path),
        "title": pdf_title(pdf_path),
        "source_path": relpath(pdf_path),
        "source_sha256": sha256_file(pdf_path),
        "extractor": "pypdf-layout-numbered-sections-v1",
        "sections": [serialize_section(section) for section in sections],
    }
    output_path = manifest_path_for(pdf_path, manifest_dir)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return output_path


def sections_from_manifest(pdf_path: Path, manifest_path: Path) -> list[PdfSection]:
    payload = json.loads(manifest_path.read_text())
    lines = extract_pdf_lines(pdf_path)
    doc_slug = slugify(pdf_path.stem)
    sections: list[PdfSection] = []
    for ordinal, item in enumerate(payload.get("sections", []), start=1):
        try:
            start = int(item["line_start"])
            end = int(item["line_end"])
        except (KeyError, TypeError, ValueError):
            continue
        if start < 0 or end > len(lines) or start >= end:
            continue
        title = normalize_space(item.get("title")) or f"Section {ordinal}"
        level = int(item.get("level") or 1)
        section = build_section(lines, doc_slug, ordinal, title, level, start, end)
        if section:
            sections.append(section)
    return sections


def load_or_draft_sections(
    pdf_path: Path,
    manifest_dir: Path,
    *,
    write_manifest: bool,
    redraft: bool,
) -> list[PdfSection]:
    manifest_path = manifest_path_for(pdf_path, manifest_dir)
    if manifest_path.exists() and not redraft:
        sections = sections_from_manifest(pdf_path, manifest_path)
        if sections:
            return sections

    sections = draft_pdf_sections(pdf_path)
    if write_manifest:
        write_section_manifest(pdf_path, sections, manifest_dir)
    return sections


def load_ontology_nodes() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    data = load_yaml(NODES_YAML)
    records: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    for group_name, node_type in NODE_GROUPS:
        for entry in data.get(group_name, []) or []:
            record = dict(entry)
            record["node_type"] = node_type
            record["description"] = normalize_space(record.get("description"))
            record["source_documents"] = record.get("source_documents") or []
            records.append(record)
            by_id[record["id"]] = record
    return records, by_id


def load_relations() -> list[dict[str, Any]]:
    data = load_yaml(RELATIONS_YAML)
    return list(data.get("relations") or [])


def flat_metadata(metadata: dict[str, Any]) -> dict[str, str | int | float | bool]:
    flat: dict[str, str | int | float | bool] = {}
    for key, value in metadata.items():
        if value is None:
            flat[key] = ""
        elif isinstance(value, (str, int, float, bool)):
            flat[key] = value
        elif isinstance(value, list):
            flat[key] = ", ".join(str(item) for item in value)
        else:
            flat[key] = json.dumps(value, ensure_ascii=False)
    return flat


def make_text_node(text: str, metadata: dict[str, Any], node_id: str):
    from llama_index.core.schema import TextNode

    return TextNode(text=text, metadata=flat_metadata(metadata), id_=node_id)


def build_pdf_text_nodes(args: argparse.Namespace) -> list[Any]:
    nodes: list[Any] = []
    for pdf_path in course_note_paths():
        doc_id = infer_doc_id(pdf_path)
        title = pdf_title(pdf_path)
        sections = load_or_draft_sections(
            pdf_path,
            Path(args.manifest_dir),
            write_manifest=True,
            redraft=args.redraft_sections,
        )
        for section in sections:
            text = (
                "Course note section\n"
                f"Document: {title}\n"
                f"Doc ID: {doc_id}\n"
                f"Section: {section.title}\n"
                f"Pages: {section.page_start}-{section.page_end}\n\n"
                f"{section.text}"
            )
            metadata = {
                "kind": "pdf_section",
                "doc_id": doc_id,
                "document_title": title,
                "section_id": section.section_id,
                "section_title": section.title,
                "section_level": section.level,
                "page_start": section.page_start,
                "page_end": section.page_end,
                "source_path": relpath(pdf_path),
                "word_count": section.word_count,
            }
            nodes.append(make_text_node(text, metadata, f"pdf:{doc_id}:{section.section_id}"))
    return nodes


def build_ontology_text_nodes() -> list[Any]:
    node_records, nodes_by_id = load_ontology_nodes()
    text_nodes: list[Any] = []

    for record in node_records:
        source_documents = record.get("source_documents") or []
        text = (
            "Ontology node\n"
            f"ID: {record['id']}\n"
            f"Type: {record['node_type']}\n"
            f"Label: {record.get('label', record['id'])}\n"
            f"Description: {record.get('description', '')}\n"
            f"Source documents: {', '.join(source_documents)}"
        )
        metadata = {
            "kind": "node",
            "node_id": record["id"],
            "label": record.get("label", record["id"]),
            "node_type": record["node_type"],
            "source_documents": source_documents,
        }
        text_nodes.append(make_text_node(text, metadata, f"node:{record['id']}"))

    for index, relation in enumerate(load_relations(), start=1):
        source = nodes_by_id.get(relation["source"], {})
        target = nodes_by_id.get(relation["target"], {})
        quote = relation.get("quote")
        quote_text = quote if quote else "None recorded; relation may be implied."
        text = (
            "Ontology relation\n"
            f"Source: {relation['source']} ({source.get('label', relation['source'])})\n"
            f"Type: {relation['type']}\n"
            f"Target: {relation['target']} ({target.get('label', relation['target'])})\n"
            f"Note: {normalize_space(relation.get('note'))}\n"
            f"Quote: {normalize_space(quote_text)}"
        )
        metadata = {
            "kind": "relation",
            "relation_type": relation["type"],
            "source_id": relation["source"],
            "source_label": source.get("label", relation["source"]),
            "target_id": relation["target"],
            "target_label": target.get("label", relation["target"]),
        }
        rel_id = f"relation:{index:04d}:{relation['source']}:{relation['type']}:{relation['target']}"
        text_nodes.append(make_text_node(text, metadata, rel_id))

    return text_nodes


def get_embed_model(model_name: str, max_length: int):
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    kwargs: dict[str, Any] = {
        "model_name": model_name,
        "trust_remote_code": True,
        "max_length": max_length,
        "query_instruction": "Query: ",
        "text_instruction": "Document: ",
        "model_kwargs": {"default_task": "retrieval"},
    }
    return HuggingFaceEmbedding(**kwargs)


def get_chroma_collection(args: argparse.Namespace, *, reset: bool = False):
    import chromadb

    persist_dir = Path(args.persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist_dir))
    if reset:
        try:
            client.delete_collection(args.collection)
        except Exception:
            pass
    return client.get_or_create_collection(
        args.collection,
        metadata={"hnsw:space": "cosine"},
    )


def write_build_manifest(args: argparse.Namespace, counts: dict[str, int]) -> None:
    DEFAULT_RAG_DIR.mkdir(parents=True, exist_ok=True)
    source_paths = [
        DOCUMENTS_YAML,
        NODES_YAML,
        RELATIONS_YAML,
        *course_note_paths(),
    ]
    payload = {
        "collection": args.collection,
        "persist_dir": display_path(args.persist_dir),
        "embedding_model": args.embed_model,
        "embedding_max_length": args.max_length,
        "counts": counts,
        "sources": [
            {
                "path": relpath(path),
                "mtime": path.stat().st_mtime,
                "sha256": sha256_file(path),
            }
            for path in source_paths
            if path.exists()
        ],
    }
    (DEFAULT_RAG_DIR / "index-manifest.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    )


def command_sections(args: argparse.Namespace) -> int:
    summaries = []
    for pdf_path in course_note_paths():
        sections = draft_pdf_sections(pdf_path)
        output_path = None
        if args.write:
            output_path = write_section_manifest(pdf_path, sections, Path(args.manifest_dir))
        summary = {
            "doc_id": infer_doc_id(pdf_path),
            "source_path": relpath(pdf_path),
            "section_count": len(sections),
            "manifest_path": relpath(output_path) if output_path else None,
            "sections": [serialize_section(section) for section in sections],
        }
        summaries.append(summary)

    if args.json:
        print(json.dumps({"documents": summaries}, indent=2, ensure_ascii=False))
    else:
        for summary in summaries:
            manifest_note = f" -> {summary['manifest_path']}" if summary["manifest_path"] else ""
            print(
                f"{summary['doc_id']}: {summary['section_count']} sections"
                f"{manifest_note}"
            )
            for section in summary["sections"]:
                print(
                    f"  p{section['page_start']}-{section['page_end']} "
                    f"{section['title']} ({section['word_count']} words)"
                )
    return 0


def selected_course_note_paths(doc_ids: list[str] | None) -> tuple[list[Path], list[str]]:
    paths = course_note_paths()
    if not doc_ids:
        return paths, []

    requested = set(doc_ids)
    selected: list[Path] = []
    for path in paths:
        doc_id = infer_doc_id(path)
        if doc_id in requested:
            selected.append(path)
            requested.remove(doc_id)
    return selected, sorted(requested)


def format_extracted_line(line: ExtractedLine) -> str:
    return f"L{line.index:04d} p{line.page}.{line.page_line}: {line.text}"


def format_line_window(
    lines: list[ExtractedLine],
    start: int,
    end: int,
) -> list[str]:
    lower = max(0, start)
    upper = min(len(lines), end)
    return [format_extracted_line(line) for line in lines[lower:upper]]


def format_section_samples(
    lines: list[ExtractedLine],
    section: PdfSection,
    sample_lines: int,
) -> tuple[list[str], list[str]]:
    start = section.line_start
    end = section.line_end
    head_end = min(end, start + sample_lines)
    tail_start = max(start, end - sample_lines)
    head = format_line_window(lines, start, head_end)
    tail = [] if tail_start <= head_end else format_line_window(lines, tail_start, end)
    return head, tail


def section_review_flags(section: PdfSection) -> list[str]:
    flags: list[str] = []
    if section.word_count < 120:
        flags.append("short_chunk")
    if section.word_count > 1200:
        flags.append("long_chunk")
    if section.line_end - section.line_start <= 4:
        flags.append("very_few_extracted_lines")
    if section.title.lower() in {"front matter", "introduction"} and section.word_count < 150:
        flags.append("possibly_heading_only")
    return flags


def load_manifest_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def manifest_review_path_for(pdf_path: Path, review_dir: Path) -> Path:
    return review_dir / f"{infer_doc_id(pdf_path)}.section-review.md"


def build_section_review_packet(
    pdf_path: Path,
    manifest_dir: Path,
    *,
    redraft: bool,
    context_lines: int,
    sample_lines: int,
) -> str:
    doc_id = infer_doc_id(pdf_path)
    manifest_path = manifest_path_for(pdf_path, manifest_dir)
    manifest_payload = load_manifest_payload(manifest_path)
    manifest_sha = manifest_payload.get("source_sha256")
    source_sha = sha256_file(pdf_path)
    source_status = "fresh" if manifest_sha == source_sha else "missing-or-stale"
    source_kind = "fresh heuristic draft" if redraft or not manifest_path.exists() else "existing manifest"
    sections = load_or_draft_sections(
        pdf_path,
        manifest_dir,
        write_manifest=False,
        redraft=redraft,
    )
    lines = extract_pdf_lines(pdf_path)

    packet: list[str] = [
        f"# Section Manifest Review: {doc_id}",
        "",
        "You are checking whether this PDF was chunked into semantically useful RAG sections.",
        "The deterministic extractor is intentionally simple and can be fooled by PDF formatting.",
        "",
        "## Task",
        "",
        "- Read the section list and boundary snippets below.",
        "- Decide whether each chunk is coherent enough for retrieval.",
        "- Prefer preserving the manifest when boundaries are acceptable.",
        "- If a boundary is wrong, edit the target manifest JSON directly.",
        "- Only edit `title`, `level`, `line_start`, and `line_end` unless a section must be added or removed.",
        "- Keep line ranges contiguous, non-overlapping, and within the extracted line numbers.",
        "- Keep the source PDF unchanged.",
        "",
        "## Target",
        "",
        f"- source_pdf: `{relpath(pdf_path)}`",
        f"- doc_id: `{doc_id}`",
        f"- title: {pdf_title(pdf_path)}",
        f"- target_manifest: `{relpath(manifest_path)}`",
        f"- source_kind: {source_kind}",
        f"- source_sha_status: {source_status}",
        f"- extracted_lines: {len(lines)}",
        f"- current_sections: {len(sections)}",
        "",
        "## Review Checklist",
        "",
        "- Does every top-level/subsection heading start a sensible chunk?",
        "- Are tiny heading-only chunks merged with their following explanatory section when useful?",
        "- Are very large sections split at meaningful internal headings or topic turns?",
        "- Do start/end snippets show missing text, duplicated text, or page-order extraction problems?",
        "- Are page ranges and titles still accurate after any edits?",
        "",
        "## Commands",
        "",
        "```bash",
        f"uv run python scripts/rag.py review-sections --doc-id {doc_id} --write",
        "uv run python scripts/rag.py index",
        "```",
        "",
        "## Current Sections",
        "",
    ]

    for ordinal, section in enumerate(sections, start=1):
        packet.extend(
            [
                f"### {ordinal:03d}. {section.title}",
                "",
                (
                    f"- level: {section.level}; pages: {section.page_start}-{section.page_end}; "
                    f"lines: {section.line_start}-{section.line_end}; words: {section.word_count}"
                ),
            ]
        )
        flags = section_review_flags(section)
        if flags:
            packet.append(f"- review_flags: {', '.join(flags)}")
        packet.extend(["", "start sample:"])
        head, tail = format_section_samples(lines, section, sample_lines)
        packet.extend(f"- `{line}`" for line in head)
        if tail:
            packet.extend(["", "end sample:"])
            packet.extend(f"- `{line}`" for line in tail)

        start_context = format_line_window(
            lines,
            section.line_start - context_lines,
            section.line_start + context_lines + 1,
        )
        end_context = format_line_window(
            lines,
            section.line_end - context_lines,
            section.line_end + context_lines + 1,
        )
        packet.extend(["", "start boundary context:"])
        packet.extend(f"- `{line}`" for line in start_context)
        packet.extend(["", "end boundary context:"])
        packet.extend(f"- `{line}`" for line in end_context)
        packet.append("")

    return "\n".join(packet).rstrip() + "\n"


def command_review_sections(args: argparse.Namespace) -> int:
    selected, missing = selected_course_note_paths(args.doc_id)
    if missing:
        print(f"Unknown doc_id(s): {', '.join(missing)}", file=sys.stderr)
        return 1
    if not selected:
        print("No course-note PDFs found.", file=sys.stderr)
        return 1

    manifest_dir = Path(args.manifest_dir)
    review_dir = Path(args.review_dir)
    packets: list[tuple[Path, str]] = []
    for pdf_path in selected:
        packet = build_section_review_packet(
            pdf_path,
            manifest_dir,
            redraft=args.redraft,
            context_lines=args.context_lines,
            sample_lines=args.sample_lines,
        )
        output_path = manifest_review_path_for(pdf_path, review_dir)
        packets.append((output_path, packet))

    if args.write:
        review_dir.mkdir(parents=True, exist_ok=True)
        for output_path, packet in packets:
            output_path.write_text(packet)
            print(f"Wrote {relpath(output_path)}")
    else:
        for index, (_, packet) in enumerate(packets):
            if index:
                print("\n---\n")
            print(packet, end="")
    return 0


def command_index(args: argparse.Namespace) -> int:
    from llama_index.core import StorageContext, VectorStoreIndex
    from llama_index.vector_stores.chroma import ChromaVectorStore

    pdf_nodes = build_pdf_text_nodes(args)
    ontology_nodes = build_ontology_text_nodes()
    all_nodes = pdf_nodes + ontology_nodes

    if not all_nodes:
        print("No RAG chunks found to index.", file=sys.stderr)
        return 1

    chroma_collection = get_chroma_collection(args, reset=True)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    with quiet_external_output(enabled=not args.progress):
        embed_model = get_embed_model(args.embed_model, args.max_length)
    VectorStoreIndex(
        all_nodes,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=args.progress,
    )

    counts = {
        "pdf_section": len(pdf_nodes),
        "ontology": len(ontology_nodes),
        "total": len(all_nodes),
    }
    write_build_manifest(args, counts)
    print(
        f"Indexed {counts['total']} chunks "
        f"({counts['pdf_section']} PDF sections, {counts['ontology']} ontology records) "
        f"into {args.collection} at {args.persist_dir}"
    )
    return 0


def ensure_db_fresh() -> None:
    source_paths = [DOCUMENTS_YAML, NODES_YAML, RELATIONS_YAML]
    if not DB_PATH.exists() or any(path.stat().st_mtime > DB_PATH.stat().st_mtime for path in source_paths):
        subprocess.run([sys.executable, "scripts/build_db.py"], cwd=ROOT, check=True)


def query_node_matches(conn: sqlite3.Connection, query: str) -> set[str]:
    lowered = query.lower()
    matches: set[str] = set()
    for node_id, label in conn.execute("SELECT id, label FROM nodes"):
        label_text = normalize_space(label).lower()
        id_text = node_id.replace("_", " ").lower()
        if len(label_text) >= 4 and label_text in lowered:
            matches.add(node_id)
        elif len(id_text) >= 4 and id_text in lowered:
            matches.add(node_id)
    return matches


def expand_graph(query: str, retrieved: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    ensure_db_fresh()
    node_ids: set[str] = set()
    for hit in retrieved:
        metadata = hit.get("metadata") or {}
        if metadata.get("kind") == "node" and metadata.get("node_id"):
            node_ids.add(str(metadata["node_id"]))
        if metadata.get("kind") == "relation":
            if metadata.get("source_id"):
                node_ids.add(str(metadata["source_id"]))
            if metadata.get("target_id"):
                node_ids.add(str(metadata["target_id"]))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    node_ids.update(query_node_matches(conn, query))
    if not node_ids:
        conn.close()
        return []

    placeholders = ",".join("?" for _ in node_ids)
    sql = f"""
        SELECT
            r.rel_type,
            r.source_id,
            source.label AS source_label,
            r.target_id,
            target.label AS target_label,
            r.note,
            r.quote
        FROM relations r
        JOIN nodes source ON source.id = r.source_id
        JOIN nodes target ON target.id = r.target_id
        WHERE r.source_id IN ({placeholders})
           OR r.target_id IN ({placeholders})
        ORDER BY r.rel_type, r.source_id, r.target_id
        LIMIT ?
    """
    params = [*node_ids, *node_ids, limit]
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def truncate(text: str, max_chars: int) -> tuple[str, bool]:
    if max_chars <= 0 or len(text) <= max_chars:
        return text, False
    return text[:max_chars].rstrip() + "\n...[truncated]", True


def serialize_retrieved(node_with_score: Any, rank: int, max_chars: int) -> dict[str, Any]:
    node = node_with_score.node
    text = getattr(node, "text", None) or node.get_content()
    text, text_truncated = truncate(text, max_chars)
    return {
        "rank": rank,
        "score": node_with_score.score,
        "id": node.node_id,
        "metadata": dict(node.metadata or {}),
        "text": text,
        "text_truncated": text_truncated,
    }


def prefixed_line(text: str, prefix: str) -> str:
    for line in text.splitlines():
        if line.startswith(prefix):
            return normalize_space(line.removeprefix(prefix))
    return ""


def retrieved_body_text(hit: dict[str, Any]) -> str:
    text = str(hit.get("text") or "")
    metadata = hit.get("metadata") or {}
    if metadata.get("kind") == "pdf_section":
        _, _, body = text.partition("\n\n")
        return normalize_space(body or text)
    return normalize_space(text)


def excerpt_text(hit: dict[str, Any], max_chars: int) -> str:
    excerpt, truncated = truncate(retrieved_body_text(hit), max_chars)
    excerpt = normalize_space(excerpt)
    if truncated:
        excerpt = excerpt.replace("...[truncated]", "... [truncated]")
    return excerpt


def format_llm_retrieved_hit(hit: dict[str, Any], excerpt_chars: int) -> list[str]:
    metadata = hit.get("metadata") or {}
    kind = metadata.get("kind") or "unknown"
    score = hit.get("score")
    try:
        score_text = f"{float(score):.4f}"
    except (TypeError, ValueError):
        score_text = "n/a"
    lines = [f"- [{hit['rank']}] {kind} score={score_text} id={hit['id']}"]

    if kind == "pdf_section":
        pages = f"pp. {metadata.get('page_start')}-{metadata.get('page_end')}"
        lines.append(
            "  source: "
            f"{metadata.get('doc_id', '')} | {metadata.get('section_title', '')} | "
            f"{pages} | {metadata.get('source_path', '')}"
        )
        lines.append(f"  excerpt: {excerpt_text(hit, excerpt_chars)}")
    elif kind == "node":
        lines.append(
            "  node: "
            f"{metadata.get('node_id', '')} ({metadata.get('label', '')}; "
            f"{metadata.get('node_type', '')})"
        )
        source_documents = metadata.get("source_documents")
        if source_documents:
            lines.append(f"  sources: {source_documents}")
        description = prefixed_line(str(hit.get("text") or ""), "Description:")
        if description:
            lines.append(f"  description: {description}")
    elif kind == "relation":
        lines.append(
            "  relation: "
            f"{metadata.get('source_id', '')} ({metadata.get('source_label', '')}) "
            f"--{metadata.get('relation_type', '')}--> "
            f"{metadata.get('target_id', '')} ({metadata.get('target_label', '')})"
        )
        note = prefixed_line(str(hit.get("text") or ""), "Note:")
        quote = prefixed_line(str(hit.get("text") or ""), "Quote:")
        if note:
            lines.append(f"  note: {note}")
        if quote and quote != "None recorded; relation may be implied.":
            lines.append(f"  quote: {quote}")
    else:
        lines.append(f"  excerpt: {excerpt_text(hit, excerpt_chars)}")

    if hit.get("text_truncated"):
        lines.append("  retrieval_text_truncated: true")
    return lines


def print_llm_query_context(
    payload: dict[str, Any],
    *,
    excerpt_chars: int,
    graph_limit: int,
) -> None:
    print(f"Query: {payload['query']}")
    print(f"Collection: {payload['collection']}")
    print(f"Embedding model: {payload['embedding_model']}")
    print()
    print("Retrieved context:")
    for hit in payload["retrieved"]:
        for line in format_llm_retrieved_hit(hit, excerpt_chars):
            print(line)

    graph = payload.get("graph_expansion") or []
    if graph:
        print()
        print(f"Graph facts (up to {graph_limit}):")
        for row in graph:
            print(
                f"- {row['source_id']} ({row['source_label']}) "
                f"--{row['rel_type']}--> {row['target_id']} ({row['target_label']}): "
                f"{normalize_space(row['note'])}"
            )
            quote = normalize_space(row.get("quote"))
            if quote:
                print(f"  quote: {quote}")


def command_query(args: argparse.Namespace) -> int:
    from llama_index.core import VectorStoreIndex
    from llama_index.vector_stores.chroma import ChromaVectorStore

    collection = get_chroma_collection(args, reset=False)
    if collection.count() == 0:
        print(
            f"Collection {args.collection!r} is empty. Run: uv run python scripts/rag.py index",
            file=sys.stderr,
        )
        return 1

    vector_store = ChromaVectorStore(chroma_collection=collection)
    with quiet_external_output():
        embed_model = get_embed_model(args.embed_model, args.max_length)
    index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
    retriever = index.as_retriever(similarity_top_k=args.top_k)
    with quiet_external_output():
        retrieved_nodes = retriever.retrieve(args.question)
    retrieved = [
        serialize_retrieved(node_with_score, rank, args.max_chars)
        for rank, node_with_score in enumerate(retrieved_nodes, start=1)
    ]
    graph = [] if args.no_graph else expand_graph(args.question, retrieved, args.graph_limit)

    payload = {
        "query": args.question,
        "collection": args.collection,
        "embedding_model": args.embed_model,
        "retrieved": retrieved,
        "graph_expansion": graph,
    }
    if args.json or args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if args.format == "llm":
        print_llm_query_context(
            payload,
            excerpt_chars=args.excerpt_chars,
            graph_limit=args.graph_limit,
        )
        return 0

    print(f"Query: {args.question}\n")
    print("Retrieved chunks:")
    for hit in retrieved:
        metadata = hit["metadata"]
        title = metadata.get("section_title") or metadata.get("label") or metadata.get("relation_type") or hit["id"]
        source = metadata.get("doc_id") or metadata.get("node_id") or metadata.get("source_id", "")
        print(f"\n[{hit['rank']}] {metadata.get('kind')} {title} ({source}) score={hit['score']:.4f}")
        print(hit["text"])

    if graph:
        print("\nGraph expansion:")
        for row in graph:
            print(
                f"- {row['source_id']} ({row['source_label']}) "
                f"{row['rel_type']} {row['target_id']} ({row['target_label']}): "
                f"{normalize_space(row['note'])}"
            )
    return 0


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--persist-dir", default=str(DEFAULT_CHROMA_DIR))
    parser.add_argument("--manifest-dir", default=str(DEFAULT_MANIFEST_DIR))
    parser.add_argument("--collection", default=DEFAULT_COLLECTION)
    parser.add_argument("--embed-model", default=DEFAULT_EMBED_MODEL)
    parser.add_argument("--max-length", type=int, default=DEFAULT_MAX_LENGTH)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build and query a local Chroma/LlamaIndex RAG index for the FAB ontology."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sections = subparsers.add_parser("sections", help="Draft logical PDF section manifests.")
    add_common_args(sections)
    sections.add_argument("--write", action="store_true", help="Write manifests under .rag/manifests.")
    sections.add_argument("--json", action="store_true", help="Print the section map as JSON.")
    sections.set_defaults(func=command_sections)

    review_sections = subparsers.add_parser(
        "review-sections",
        help="Generate LLM-facing review packets for section manifests.",
    )
    add_common_args(review_sections)
    review_sections.add_argument(
        "--doc-id",
        action="append",
        help="Limit review to a document ID. Repeat to review multiple documents.",
    )
    review_sections.add_argument(
        "--review-dir",
        default=str(DEFAULT_REVIEW_DIR),
        help="Directory for written review packets.",
    )
    review_sections.add_argument(
        "--write",
        action="store_true",
        help="Write review packets under .rag/reviews instead of printing them.",
    )
    review_sections.add_argument(
        "--redraft",
        action="store_true",
        help="Review a fresh heuristic draft instead of the existing manifest.",
    )
    review_sections.add_argument(
        "--context-lines",
        type=int,
        default=2,
        help="Number of surrounding extracted lines to show around boundaries.",
    )
    review_sections.add_argument(
        "--sample-lines",
        type=int,
        default=3,
        help="Number of start/end lines to sample from each section.",
    )
    review_sections.set_defaults(func=command_review_sections)

    index = subparsers.add_parser("index", help="Rebuild the local Chroma vector index.")
    add_common_args(index)
    index.add_argument("--redraft-sections", action="store_true", help="Ignore existing section manifests.")
    index.add_argument("--progress", action="store_true", help="Show embedding progress.")
    index.set_defaults(func=command_index)

    query = subparsers.add_parser("query", help="Retrieve RAG context for a natural-language question.")
    add_common_args(query)
    query.add_argument("question")
    query.add_argument("--top-k", type=int, default=8)
    query.add_argument(
        "--format",
        choices=("text", "llm", "json"),
        default="llm",
        help="Output style: llm for compact context, text for verbose reading, json for full metadata.",
    )
    query.add_argument("--json", action="store_true", help="Deprecated alias for --format json.")
    query.add_argument("--max-chars", type=int, default=6000)
    query.add_argument(
        "--excerpt-chars",
        type=int,
        default=900,
        help="Maximum characters per retrieved excerpt in --format llm output.",
    )
    query.add_argument("--no-graph", action="store_true")
    query.add_argument("--graph-limit", type=int, default=30)
    query.set_defaults(func=command_query)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
