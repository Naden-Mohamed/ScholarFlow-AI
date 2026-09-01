def recall_at_k(retrieved_ids: list[int], target_id: int, k: int) -> int:
    """
    Measures what fraction of queries successfully retrieve
    the target document within the top-k results
    """
    top_k = retrieved_ids[:k]
    return 1 if target_id in top_k else 0


def hit_rate_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> int:
    """
    Measures the fraction of queries or users
    where at least one relevant item appears anywhere in the top-k results.
    """
    return int(bool(set(retrieved_ids[:k]) & relevant_ids))


def reciprocal_rank(retrieved_ids: list[int], target_id: int) -> float:
    """
    measures how well target document were ranked
    """
    try:
        rank = retrieved_ids.index(target_id) + 1  # 1-indexed to avoid dividing by 0
        return 1.0 / rank

    except ValueError:
        return 0.0
