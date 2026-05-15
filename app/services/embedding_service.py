import math
import re
from collections import Counter


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
    "you",
    "your",
}


def tokenize_text(text: str) -> list[str]:
    """Return normalized tokens that are useful for resume/job matching."""
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]*", text.lower())
    return [token for token in tokens if token not in STOP_WORDS and len(token) > 1]


def build_term_vector(text: str) -> Counter[str]:
    return Counter(tokenize_text(text))


def cosine_similarity(first_text: str, second_text: str) -> float:
    first_vector = build_term_vector(first_text)
    second_vector = build_term_vector(second_text)

    if not first_vector or not second_vector:
        return 0.0

    common_terms = first_vector.keys() & second_vector.keys()
    dot_product = sum(first_vector[term] * second_vector[term] for term in common_terms)
    first_magnitude = math.sqrt(sum(value * value for value in first_vector.values()))
    second_magnitude = math.sqrt(sum(value * value for value in second_vector.values()))

    if not first_magnitude or not second_magnitude:
        return 0.0

    return dot_product / (first_magnitude * second_magnitude)


def extract_matching_keywords(first_text: str, second_text: str, limit: int = 12) -> list[str]:
    first_terms = build_term_vector(first_text)
    second_terms = build_term_vector(second_text)
    shared_terms = first_terms.keys() & second_terms.keys()

    ranked_terms = sorted(
        shared_terms,
        key=lambda term: first_terms[term] + second_terms[term],
        reverse=True,
    )
    return ranked_terms[:limit]


def score_text_similarity(first_text: str, second_text: str) -> int:
    return round(cosine_similarity(first_text, second_text) * 100)
