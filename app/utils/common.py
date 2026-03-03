from typing import TypeVar

T = TypeVar("T")


def ensure_found(obj: T | None):
    if obj is None:
        raise ValueError("Not found")


def normalize_limit(raw_limit: int | None) -> int:
    default_limit = 20
    max_limit = 100
    limit = default_limit if raw_limit is None else min(raw_limit, max_limit)

    if limit <= 0:
        raise ValueError("Limit must be a positive integer")

    return limit
