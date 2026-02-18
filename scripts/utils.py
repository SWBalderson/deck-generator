#!/usr/bin/env python3
"""Shared utility functions for deck-generator scripts."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]{2,}")

STOP_WORDS = frozenset({
    'the', 'and', 'for', 'with', 'from', 'that', 'this', 'will', 'have', 'has',
    'are', 'was', 'were', 'into', 'their', 'about', 'where', 'which', 'using',
    'through', 'more', 'than', 'over', 'each', 'across', 'while', 'when',
    'under', 'between', 'after', 'before',
})


def normalise_words(text: str) -> List[str]:
    """Extract meaningful words from text, filtering stop words."""
    return [w.lower() for w in WORD_RE.findall(text or '') if w.lower() not in STOP_WORDS]


def jaccard(a: set, b: set) -> float:
    """Jaccard similarity coefficient between two sets."""
    if not a or not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def build_content_index(content: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Index ingested documents by both full path and basename for lookup."""
    indexed: Dict[str, Dict[str, Any]] = {}
    for path, item in content.get('contents', {}).items():
        indexed[path] = item
        indexed[Path(path).name] = item
        filename = item.get('filename')
        if isinstance(filename, str):
            indexed[filename] = item
    return indexed


def extract_records(document: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract tabular row records from an ingested document payload."""
    if not document:
        return []

    data = document.get('data')
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]

    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                return value

    return []


def to_float(value: Any) -> Optional[float]:
    """Convert a value to float when possible, stripping commas and percent signs."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(',', '').replace('%', '').strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def load_json(path: Path) -> Any:
    """Load and parse a JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path: Path, payload: Any) -> None:
    """Write a payload as formatted JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def split_fragments(text: str) -> List[str]:
    """Split text into sentence-level fragments."""
    parts = re.split(r'(?<=[.!?])\s+|\n+', text or '')
    return [p.strip() for p in parts if p and p.strip()]


def extract_source_text(doc: Dict[str, Any]) -> str:
    """Extract the best available text representation from an ingested document."""
    if not doc:
        return ''
    for key in ['content', 'text', 'markdown']:
        value = doc.get(key)
        if isinstance(value, str) and value.strip():
            return value
    data = doc.get('data')
    if data is not None:
        return json.dumps(data, ensure_ascii=False)
    return ''
