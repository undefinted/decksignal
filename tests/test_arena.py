from helpers import write_json

from openpptbench.arena import aggregate_elo


def test_arena_elo_ranks_consistent_winner_first(tmp_path):
    reviews = []
    for index in range(3):
        reviews.append(
            {
                "review_id": str(index),
                "task_id": "task",
                "left_submission_id": "alpha",
                "right_submission_id": "beta",
                "choices": {
                    "content": "left",
                    "visual": "left",
                    "ready_to_use": "left",
                },
                "reviewer_group": "general",
                "created_at": f"2026-09-01T00:00:0{index}Z",
            }
        )
    source = write_json(tmp_path / "reviews.json", reviews)

    result = aggregate_elo(source)

    assert result["rows"][0]["submission_id"] == "alpha"
    assert result["rows"][0]["rating"] > 1000
    assert result["rows"][0]["provisional"] is True


def test_arena_rejects_self_comparison(tmp_path):
    source = write_json(
        tmp_path / "reviews.json",
        {
            "review_id": "bad",
            "left_submission_id": "same",
            "right_submission_id": "same",
            "choices": {"content": "tie", "visual": "tie", "ready_to_use": "tie"},
            "created_at": "2026-09-01T00:00:00Z",
        },
    )
    try:
        aggregate_elo(source)
    except ValueError as exc:
        assert "itself" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

