# Ranking model draft

## Why a simple weighted average is invalid

Benchmarks differ in task, scale, evaluator, language, artifact format, and date. A score of 80 from one project is not automatically better than 75 from another. OpenPPTBench therefore stores native scores and constructs normalized evidence only within defensible comparison groups.

## Normalized observation

For an observation `i` mapped to capability `c`:

```text
normalized_score_i = normalize_within_source_and_version(raw_score_i)
effective_weight_i = source_reliability_i * freshness_i * sample_quality_i
```

Freshness is initially modeled as exponential decay:

```text
freshness_i = 2 ^ (-age_days / half_life_days)
```

Recommended initial half-lives:

- commercial web product behavior: 90 days;
- price and plan facts: 30 days;
- open-source pinned release: 180 days;
- stable artifact-conformance metrics: 180 days;
- human preference result: 120 days.

These are policy defaults, not scientific constants, and must be calibrated from observed product changes.

## Capability score

Within a valid comparison group:

```text
capability_score = weighted_mean(normalized_score_i, effective_weight_i)
```

Also publish:

- effective sample size;
- date of newest and oldest qualifying evidence;
- number of independent evidence sources;
- uncertainty or confidence interval;
- benchmark and scenario coverage.

## Coverage

Coverage is a vector, not merely a percentage. At minimum it records evaluated tracks, scenarios, languages, artifact formats, and capabilities. A convenient display percentage may be calculated against a selected leaderboard's requirements.

Products below the leaderboard's minimum evidence threshold are shown as `insufficient evidence`, even when an observed score is high.

## Overall index

An overall index can be computed only when:

- all required capabilities have current evidence;
- at least two independent evidence sources contribute;
- at least one source is a reproducible run;
- minimum task and human-vote counts are met.

The index must display its weight profile. Users should be able to switch profiles such as `business`, `education`, `native-editing`, and `budget`.

## Pairwise arena

Human preference is modeled separately using Bradley–Terry or another documented pairwise model. Arena ratings are not silently converted into rubric scores. They may contribute as one evidence family after minimum vote count, reviewer-quality checks, and uncertainty reporting.

