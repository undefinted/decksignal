import importlib.util
import json
from pathlib import Path

from pptx import Presentation


def test_intake_rejects_changed_artifact(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('pilot_runner', root / 'scripts/run_pilot.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    monkeypatch.setattr(runner, 'ROOT', tmp_path)
    folder = tmp_path / 'inputs' / 'tool' / 'task'
    folder.mkdir(parents=True)
    Presentation().save(folder / 'deck.pptx')
    manifest = {
        'schema_version': '0.1.0', 'submission_id': 'tool-task',
        'task_id': 'task', 'track': 'pilot',
        'product': {'name': 'tool', 'provider': 'provider', 'plan': 'test'},
        'run': {'started_at': '2026-09-11T00:00:00Z',
                'completed_at': '2026-09-11T00:01:00Z',
                'attempt': 1, 'locale': 'en', 'manual_edits': False},
        'artifact': {'format': 'pptx', 'sha256': '0' * 64, 'redistribution': 'allowed'},
    }
    (folder / 'submission.json').write_text(json.dumps(manifest), encoding='utf-8')
    monkeypatch.setattr('sys.argv', ['run_pilot', '--input', 'inputs', '--output', 'outputs',
                                    '--schema', str(root / 'benchmark/schema/submission.schema.json')])
    assert runner.main() == 1
    report = json.loads((tmp_path / 'outputs/pilot-report.json').read_text())
    assert report['runs'][0]['status'] == 'hash_mismatch'
    assert not list((tmp_path / 'outputs').glob('*.metrics.json'))
