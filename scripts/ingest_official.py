from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from app.ingestion import ingest_document


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest an official SchemeAI PDF/HTML source into provenance-tagged JSONL")
    parser.add_argument("source", help="Local PDF/HTML/text path or official HTTP(S) URL")
    parser.add_argument("--authority", required=True)
    parser.add_argument("--official-url", required=True)
    parser.add_argument("--document-title", required=True)
    parser.add_argument("--last-verified", required=True, help="YYYY-MM-DD")
    parser.add_argument("--scheme-id", required=True)
    parser.add_argument("--scheme-name", required=True)
    parser.add_argument("--scheme-type", choices=["scholarship", "education_support"], default="scholarship")
    parser.add_argument("--output", default="data/official/ingested.jsonl")
    args = parser.parse_args()

    record, result = ingest_document(
        source=args.source,
        authority=args.authority,
        official_url=args.official_url,
        document_title=args.document_title,
        last_verified=date.fromisoformat(args.last_verified),
        scheme_id=args.scheme_id,
        scheme_name=args.scheme_name,
        scheme_type=args.scheme_type,
    )

    if result.rejected:
        for issue in result.issues:
            print(f"{issue.level.upper()}: {issue.message} [{issue.source}]")
        raise SystemExit(2)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as handle:
        handle.write(record.model_dump_json() + "\n")
    print(f"Accepted {result.accepted} provenance-tagged chunks -> {output}")


if __name__ == "__main__":
    main()
