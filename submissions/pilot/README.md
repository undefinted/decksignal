# Pilot submission dropzone

Put one run in `<product>/<task>/`:

```text
submission.json
deck.pptx                 # or another artifact format declared in the manifest
```

Copy the manifest shape from `benchmark/schema/submission.schema.json`. The
`artifact.path` is relative to the manifest directory; omit it to use the
default filename `deck.pptx`.

Run the local, non-scoring checks from the repository root:

```powershell
python scripts/run_pilot.py
```

The report is written to `results/raw/pilot/pilot-report.json`. PPTX files get
native structural metrics. No leaderboard score is produced until the required
content, visual, editing, and operations evidence is present and reviewed.
