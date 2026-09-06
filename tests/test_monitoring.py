from helpers import write_json

from openpptbench.monitoring import merge_discoveries


def test_merge_discoveries_deduplicates_candidates(tmp_path):
    record = {
        "candidate_id": "one",
        "name": "One",
        "url": "https://example.com",
    }
    source = write_json(tmp_path / "incoming.json", [record, record])
    queue = tmp_path / "queue.json"

    first = merge_discoveries(source, queue)
    second = merge_discoveries(source, queue)

    assert first == {"added": 1, "total": 1, "queue": str(queue)}
    assert second["added"] == 0

