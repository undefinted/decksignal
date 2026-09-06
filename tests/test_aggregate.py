import json

from openpptbench.aggregate import aggregate


def test_aggregate_ranks_higher_score_first(tmp_path):
    base = {
        "task_id": "opb-business-001",
        "track": "prompt_to_deck",
        "product": {"plan": "free"},
        "run": {"completed_at": "2026-09-06T00:00:00Z"},
    }
    submissions = []
    for name, value in [("Alpha", 4), ("Beta", 3)]:
        submission = json.loads(json.dumps(base))
        submission.update({"submission_id": name.lower()})
        submission["product"].update({"name": name})
        submission["scores"] = {
            "content_quality": value,
            "narrative_quality": value,
            "visual_quality": value,
            "instruction_following": value,
            "editability": value,
            "user_experience": value,
        }
        submissions.append(submission)
    source = tmp_path / "submissions.json"
    source.write_text(json.dumps(submissions), encoding="utf-8")

    result = aggregate(source)

    assert [row["product"] for row in result["products"]] == ["Alpha", "Beta"]
    assert result["products"][0]["weighted_score"] == 4


def test_aggregate_rejects_missing_dimensions(tmp_path):
    source = tmp_path / "submissions.json"
    source.write_text(
        json.dumps(
            {
                "submission_id": "broken",
                "task_id": "opb-business-001",
                "track": "prompt_to_deck",
                "product": {"name": "Broken", "plan": "free"},
                "run": {"completed_at": "2026-09-06T00:00:00Z"},
                "scores": {"content_quality": 3},
            }
        ),
        encoding="utf-8",
    )

    try:
        aggregate(source)
    except ValueError as exc:
        assert "Missing score dimensions" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

