"""
evaluate.py
Runs all 5 evaluation questions from planning.md against the RAG system
and outputs a structured report to evaluation_report.txt.
"""

import json
from pathlib import Path
from query import query

EVAL_QUESTIONS = [
    {
        "id": 1,
        "question": "What is the full-time graduate tuition for the 2025-2026 academic year?",
        "expected": "$66,670",
    },
    {
        "id": 2,
        "question": "How does a student begin the process of requesting disability accommodations at JHU?",
        "expected": "Complete the online SDS Application and provide documentation meeting SDS Guidelines for Documentation",
    },
    {
        "id": 3,
        "question": "What is the non-refundable fee charged when registering for courses at the School of Education?",
        "expected": "$175",
    },
    {
        "id": 4,
        "question": "What is the Dissertation Prize Fellowship and who is eligible for it?",
        "expected": "A fellowship for final-year KSAS students to focus on dissertation writing without teaching obligations for a semester; students beyond their sixth year in spring 2025 are ineligible",
    },
    {
        "id": 5,
        "question": "What happens to a School of Education student who fails to enroll each semester and does not receive an approved leave of absence?",
        "expected": "They are made inactive and dropped from the rolls in the second week after the start of the semester, and must reapply for admission",
    },
]

OUTPUT_FILE = Path("evaluation_report.txt")


def run_evaluation():
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("EVALUATION REPORT: JHU Unofficial Guide RAG System")
    report_lines.append("=" * 70)

    results = []

    for item in EVAL_QUESTIONS:
        print(f"\nRunning Q{item['id']}: {item['question'][:60]}...")
        result = query(item["question"], verbose=False)

        report_lines.append(f"\n{'='*70}")
        report_lines.append(f"Q{item['id']}: {item['question']}")
        report_lines.append(f"\nExpected answer:\n  {item['expected']}")
        report_lines.append(f"\nSystem response:\n{result['answer']}")
        report_lines.append(f"\nChunks retrieved:")
        for i, (chunk, source) in enumerate(zip(result["chunks"], result["sources"])):
            report_lines.append(f"  [{i+1}] {source}")
            report_lines.append(f"       {chunk[:150]}...")
        report_lines.append(f"\nAccuracy (fill in manually): [ ] Accurate  [ ] Partially accurate  [ ] Inaccurate")
        report_lines.append(f"Notes: ")

        results.append({
            "id": item["id"],
            "question": item["question"],
            "expected": item["expected"],
            "answer": result["answer"],
            "sources": result["sources"],
        })

    report_lines.append(f"\n{'='*70}")
    report_lines.append("END OF REPORT")

    report_text = "\n".join(report_lines)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report_text)

    # Also save raw results as JSON
    with open("evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nReport saved to {OUTPUT_FILE}")
    print(f"Raw results saved to evaluation_results.json")
    print("\nOpen evaluation_report.txt and fill in the accuracy ratings manually.")


if __name__ == "__main__":
    run_evaluation()
