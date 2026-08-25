from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path

from sklearn.metrics import precision_recall_fscore_support

from app.data import DEMO_SCHEMES, SCHEMES
from app.eligibility import evaluate
from app.models import StudentProfile
from app.rag import retrieve

LABELS = ["LIKELY_ELIGIBLE", "POSSIBLY_ELIGIBLE", "UNKNOWN", "NOT_ELIGIBLE"]
ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests" / "eval" / "cases.jsonl"
REPORT_DIR = ROOT / "reports"


def load_cases():
    return [json.loads(line) for line in CASES.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--retrieval-mode", choices=["dense", "lexical"], default=os.getenv("SCHEMEAI_EVAL_RETRIEVAL_MODE", "lexical"))
    args = parser.parse_args()
    os.environ["SCHEMEAI_RETRIEVAL_MODE"] = args.retrieval_mode

    schemes = {s.id: s for s in [*DEMO_SCHEMES, *SCHEMES]}
    cases = load_cases()
    y_true, y_pred = [], []
    false_positives = []
    citation_hits = 0
    citation_total = 0
    citation_valid = 0

    for case in cases:
        scheme = schemes[case["scheme_id"]]
        profile = StudentProfile.model_validate(case["profile"])
        result = evaluate(profile, scheme)
        y_true.append(case["expected_status"])
        y_pred.append(result.status)

        if case["expected_status"] == "NOT_ELIGIBLE" and result.status in {"LIKELY_ELIGIBLE", "POSSIBLY_ELIGIBLE"}:
            false_positives.append({
                "case_id": case["id"],
                "scheme_id": case["scheme_id"],
                "predicted": result.status,
                "expected": case["expected_status"],
            })

        if case.get("retrieval_query"):
            evidence = retrieve(case["retrieval_query"], top_k=5)
            citation_total += 1
            if any(e.scheme_id == case.get("expected_evidence_scheme_id") for e in evidence):
                citation_hits += 1
            citation_valid += sum(
                bool(e.provenance.authority and e.provenance.official_url and e.provenance.last_verified and e.provenance.reference)
                for e in evidence
            )

    precision, recall, _, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=LABELS, zero_division=0
    )
    metrics = {
        "case_count": len(cases),
        "tier_metrics": {
            label: {"precision": round(float(precision[i]), 4), "recall": round(float(recall[i]), 4)}
            for i, label in enumerate(LABELS)
        },
        "citation_precision": round(citation_valid / max(1, sum(len(retrieve(c.get("retrieval_query"), 5)) for c in cases if c.get("retrieval_query"))), 4),
        "citation_hit_rate": round(citation_hits / max(1, citation_total), 4),
        "false_positive_count": len(false_positives),
        "false_positives": false_positives,
        "retrieval_mode": args.retrieval_mode,
        "note": "citation_precision is a provenance-validity proxy at retrieval level; claim-level citation precision requires an LLM response plus claim extraction and is added in the multilingual/LLM evaluation phase.",
    }

    REPORT_DIR.mkdir(exist_ok=True)
    (REPORT_DIR / "eval-latest.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    if false_positives:
        with (REPORT_DIR / "false_positives.jsonl").open("w", encoding="utf-8") as handle:
            for item in false_positives:
                handle.write(json.dumps(item) + "\n")

    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
