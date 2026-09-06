# Reproducibility protocol

For every evaluation unit, preserve:

- task ID and task-set version;
- exact submitted prompt and input assets;
- product, provider, visible model/version, plan, and product URL;
- account locale and interface language;
- every non-default setting;
- UTC start and completion timestamps;
- attempt number and retry reason;
- generation duration and export duration;
- original artifact checksum;
- native output when redistribution is allowed;
- rendered slide images;
- raw automated metrics;
- human-review records without personal identifiers.

The canonical main-track result is the first successfully generated, unedited output. A separate `best_effort` track may allow prompt iteration or manual configuration, but it must include a complete action log and may not be merged into the main leaderboard.

## Technical failure

A retry is permitted for a service error, timeout, corrupted download, or output that cannot be opened. Poor content, unattractive design, or ignored instructions are evaluation outcomes—not technical failures.

## Artifact redistribution

Before publishing a generated file, check the product terms and licenses of supplied assets. When redistribution is not permitted, publish the checksum, permitted screenshots, run metadata, and measurements, and set `redistribution` accordingly in the manifest.

