"""Project paths shared by scripts, servers, and generators."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DB_PATH = ROOT / "ontology.db"

DOCS_DIR = ROOT / "docs"
COURSE_NOTES_DIR = DOCS_DIR / "course-notes"

KNOWLEDGE_BASE_DIR = ROOT / "knowledge-base"
DOCUMENTS_YAML = KNOWLEDGE_BASE_DIR / "documents.yaml"
NODES_YAML = KNOWLEDGE_BASE_DIR / "nodes.yaml"
RELATIONS_YAML = KNOWLEDGE_BASE_DIR / "relations.yaml"
RELATION_SCHEMA_YAML = KNOWLEDGE_BASE_DIR / "relation-schema.yaml"
MASTERY_YAML = KNOWLEDGE_BASE_DIR / "mastery.yaml"
PRIORITY_YAML = KNOWLEDGE_BASE_DIR / "study_priority.yaml"
SCHEDULE_YAML = KNOWLEDGE_BASE_DIR / "study_schedule.yaml"

ARTIFACTS_DIR = ROOT / "artifacts"
WEB_DIR = ROOT / "web"

DEFAULT_RAG_DIR = ROOT / ".rag"
DEFAULT_CHROMA_DIR = DEFAULT_RAG_DIR / "chroma"
DEFAULT_MANIFEST_DIR = DEFAULT_RAG_DIR / "manifests"
DEFAULT_REVIEW_DIR = DEFAULT_RAG_DIR / "reviews"

