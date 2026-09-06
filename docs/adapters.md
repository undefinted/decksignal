# Benchmark adapter contract

An adapter is responsible for provenance-preserving import, not for silently making unlike scores comparable.

## Required process

1. Pin the upstream repository commit, dataset revision, evaluator version, and judge model.
2. Run the official evaluator or import a published result with artifacts.
3. Preserve all upstream raw outputs.
4. Export one row per product snapshot and mapped capability.
5. Document normalization and mapping assumptions.
6. Validate generated evidence records before ranking.

## Normalized CSV interchange

Required columns:

- `product_snapshot_id`
- `capability`
- `raw_score`
- `raw_scale`
- `normalized_score` from 0 to 100
- `sample_size`
- `observed_at`

Optional columns:

- `evidence_id`
- `track`, `scenario`, `language`, `task_ids` separated by `|`
- `uncertainty`
- `confidence_class`
- `artifacts_available`
- `artifact_refs` separated by `|`
- `notes`

Example:

```bash
openpptbench import-csv upstream.csv \
  --source slidesgen-bench \
  --source-version <commit-or-release> \
  --output-dir data/evidence
```

The importer assumes the adapter author has already performed a justified within-source normalization. It deliberately refuses to guess how an arbitrary upstream scale should map to 0–100.

