#!/usr/bin/env python3
"""Minimal, dependency-free baseline for grounded personal-profile Q&A."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


STOPWORDS = {
    "a", "an", "and", "are", "at", "did", "do", "does", "for", "from",
    "go", "i", "in", "is", "me", "my", "of", "on", "the", "to", "was",
    "s", "what", "where", "which", "who", "with", "you", "your",
}

QUERY_EXPANSIONS = {
    "college": {"education", "university", "bachelor", "master", "phd"},
    "school": {"education", "university", "bachelor", "master", "phd"},
    "study": {"education", "university", "bachelor", "master", "phd"},
    "work": {"experience", "engineer", "manager", "amazon", "axon"},
    "job": {"experience", "engineer", "manager", "amazon", "axon"},
}


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if token not in STOPWORDS
    }


def query_terms(question: str) -> set[str]:
    terms = tokenize(question)
    expanded = set(terms)
    for term in terms:
        expanded.update(QUERY_EXPANSIONS.get(term, set()))
    return expanded


def load_evidence(profile_path: Path) -> list[str]:
    lines = []
    for raw_line in profile_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip().lstrip("-*• ")
        if len(line) >= 4 and not re.fullmatch(r"[A-Za-z &/]+", line):
            lines.append(line)
    return lines


def retrieve(question: str, evidence: list[str], limit: int = 5) -> list[str]:
    terms = query_terms(question)
    scored = []
    for position, line in enumerate(evidence):
        overlap = terms & tokenize(line)
        if overlap:
            scored.append((len(overlap), -position, line))
    scored.sort(reverse=True)
    return [line for _, _, line in scored[:limit]]


def education_answer(profile_text: str) -> tuple[str, list[str]] | None:
    universities = []
    for line in profile_text.splitlines():
        line = line.strip()
        if "University" in line and not line.startswith("Logo for ") and line not in universities:
            universities.append(line)
    if not universities:
        return None
    if len(universities) == 1:
        answer = f"I studied at {universities[0]}."
    else:
        answer = f"I studied at {', '.join(universities[:-1])}, and {universities[-1]}."
    return answer, universities


def answer_question(question: str, profile_path: Path) -> dict[str, object]:
    profile_text = profile_path.read_text(encoding="utf-8")
    lowered = question.lower()

    if any(word in lowered for word in ("college", "education", "school", "study")):
        education = education_answer(profile_text)
        if education:
            answer, evidence = education
            return {"question": question, "answer": answer, "evidence": evidence}

    evidence = retrieve(question, load_evidence(profile_path))
    if not evidence:
        return {
            "question": question,
            "answer": "I don't know based on the provided profile.",
            "evidence": [],
        }
    return {
        "question": question,
        "answer": f"The profile contains this relevant fact: {evidence[0]}",
        "evidence": evidence,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True, help="UTF-8 profile text")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--question", help="Question to answer")
    group.add_argument("--input", type=Path, help="Text file containing one question")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    question = args.question or args.input.read_text(encoding="utf-8").strip()
    result = answer_question(question, args.profile)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
