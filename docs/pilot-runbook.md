# Pilot runbook

The pilot is designed to test the benchmark before it tests the market.

## Pilot matrix

Run three products on two tasks:

| Slot | Product type | Suggested candidate |
|---|---|---|
| P1 | Chinese end-user product | WPS AiPPT or 讯飞智文 |
| P2 | International end-user product | Gamma or Beautiful.ai |
| P3 | Open-source system | Presenton |

Use tasks:

- `opb-business-001`: numerical fidelity and management narrative;
- `opb-education-001`: explanation quality, safety, and audience adaptation.

This produces six decks—enough to discover broken fields, ambiguous rubric language, and artifact-handling problems without wasting dozens of paid generations.

## Before each run

- Confirm the product is available and record the canonical URL.
- Capture the displayed plan, limits, export options, interface language, and model/version if shown.
- Create a fresh submission manifest.
- Prepare a screen recording or timestamped action log if the product workflow is not reproducible through an API.
- Do not paste secrets, customer documents, or personal data.

## During each run

1. Start the timer immediately before submitting the exact task prompt.
2. Keep all settings at their defaults.
3. Do not edit an AI-generated outline unless the product requires confirmation without changes.
4. Record warnings, failures, required choices, and retry reasons.
5. Stop the generation timer when the complete deck becomes viewable.
6. Export the native artifact and record export time separately.

## After each run

1. Calculate SHA-256 for the original artifact.
2. Run the native inspector when the output is PPTX.
3. Render slides consistently before human review.
4. Complete task-specific binary checks before holistic scoring.
5. Blind product identity and randomize order for comparison.
6. Record redistribution restrictions.

## Local intake command

Drop manifests and artifacts under `submissions/pilot/<product>/<task>/`, then
run `.venv/Scripts/python.exe scripts/run_pilot.py` (or `python` after
installing the project dependencies). This validates every manifest and writes
native PPTX inspection metrics to `results/raw/pilot/`. The command is a
readiness check, not a score generator: missing external benchmark layers are
reported as pending and cannot enter a leaderboard.

## Pilot exit criteria

Do not expand beyond the pilot until:

- all six run manifests validate;
- all artifacts can be consistently stored or represented under their terms;
- two independent reviewers can use the rubric without clarification;
- obvious failures appear in raw measurements or task-specific checks;
- the results can be regenerated from committed manifests and score records.
