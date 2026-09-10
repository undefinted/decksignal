# Contributing

## Add a task

Create a YAML file in `benchmark/tasks/` that validates against `benchmark/schema/task.schema.json`. A task should describe a realistic audience and decision, avoid relying on unstable facts, and include objective required elements.

## Submit a product result

1. Run an existing benchmark task using the published protocol.
2. Copy `submissions/example.manifest.json` and record all run details.
3. Run `decksignal inspect deck.pptx --output metrics.json`.
4. Submit the manifest, metrics, permitted artifacts, and checksums.

Never include account tokens, cookies, personal information, or proprietary input documents.

## Add an evaluator

Evaluators must document their intended meaning, failure modes, and output range. New automated metrics need tests and must remain visible as raw measurements before they can affect a composite score.
