"""Minimal local knowledge ingestion helper.

Usage: python scripts/ingest.py path/to/file.txt
It creates a JSONL chunk file. Production should replace this with PDF parsing,
embeddings, vector storage, reranking and provenance validation.
"""
import json, re, sys
from pathlib import Path


def chunks(text, size=800, overlap=120):
    words = re.findall(r"\S+", text)
    out = []
    step = max(1, size - overlap)
    for i in range(0, len(words), step):
        part = " ".join(words[i:i+size])
        if part: out.append(part)
        if i + size >= len(words): break
    return out

if __name__ == "__main__":
    if len(sys.argv) != 2: raise SystemExit("Usage: python scripts/ingest.py FILE")
    p = Path(sys.argv[1])
    text = p.read_text(encoding="utf-8")
    out = p.with_suffix(p.suffix + ".chunks.jsonl")
    with out.open("w", encoding="utf-8") as f:
        for n, chunk in enumerate(chunks(text)):
            f.write(json.dumps({"chunk_id": n, "source": p.name, "text": chunk}, ensure_ascii=False) + "\n")
    print(out)
