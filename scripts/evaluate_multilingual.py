from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from app.language import detect_supported_language
from app.rag import retrieve

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests" / "eval" / "multilingual_queries.jsonl"


def main() -> int:
    rows = [json.loads(line) for line in CASES.read_text(encoding="utf-8").splitlines() if line.strip()]
    stats = defaultdict(lambda: {"total": 0, "hits": 0, "language_detection_hits": 0})
    for row in rows:
        language = row["language"]
        stats[language]["total"] += 1
        if detect_supported_language(row["query"]) == language:
            stats[language]["language_detection_hits"] += 1
        evidence = retrieve(row["query"], top_k=5)
        if any(item.scheme_id == row["expected_scheme_id"] for item in evidence):
            stats[language]["hits"] += 1

    output = {}
    for language, values in stats.items():
        output[language] = {
            **values,
            "retrieval_hit_rate": round(values["hits"] / max(1, values["total"]), 4),
            "language_detection_rate": round(values["language_detection_hits"] / max(1, values["total"]), 4),
        }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    print("Human-review status: pending native-speaker sanity check for Kannada/Hindi explanations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
