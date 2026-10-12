"""Word n-gram helpers shared by the echo, canary, and verbatim checks."""
from __future__ import annotations

import re

_TOKEN = re.compile(r"[a-z0-9']+")


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def ngram_set(text: str, n: int) -> set[tuple[str, ...]]:
    tokens = tokenize(text)
    return {tuple(tokens[index : index + n]) for index in range(len(tokens) - n + 1)} if len(tokens) >= n else set()


def shared_ngrams(a: str, b: str, n: int) -> set[tuple[str, ...]]:
    return ngram_set(a, n) & ngram_set(b, n)


def _span_regex(gram: tuple[str, ...]) -> re.Pattern[str]:
    parts = [re.escape(word) for word in gram]
    return re.compile(r"\b" + r"[\W_]*".join(parts) + r"\b", re.IGNORECASE)


def extract_span(response: str, gram: tuple[str, ...]) -> str:
    match = _span_regex(gram).search(response)
    return match.group(0) if match is not None else " ".join(gram)


def longest_common_run(response: str, snippet: str, minimum: int) -> tuple[str, tuple[str, ...]]:
    """Return the longest consecutive word run shared with a snippet."""
    response_tokens = tokenize(response)
    snippet_tokens = tokenize(snippet)
    maximum = min(len(response_tokens), len(snippet_tokens))
    for size in range(maximum, minimum - 1, -1):
        snippet_grams = ngram_set(snippet, size)
        candidates = {
            tuple(response_tokens[index : index + size])
            for index in range(len(response_tokens) - size + 1)
        }
        hits = candidates & snippet_grams
        if hits:
            gram = max(hits, key=lambda item: item[0])
            return extract_span(response, gram), gram
    return "", ()