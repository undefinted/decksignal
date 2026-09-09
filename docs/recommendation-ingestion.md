# Online recommendation ingestion

Social posts, videos, newsletters, and tutorials are discovery sources—not evaluation results.

## Capture

For every source, record:

- stable or canonical URL;
- platform, title, author, content type, and capture time;
- whether the source was fully captured, partial, inaccessible, or removed;
- each factual or evaluative claim as a separate record;
- disclosed sponsorship, affiliate links, or product relationship when visible.

Do not bypass access controls or redistribute copyrighted videos. Store a short factual description, extracted workflow facts, and permitted screenshots or quotations only when necessary.

## Claim extraction

Classify each claim as:

- tool recommendation;
- workflow or method;
- quality claim;
- price claim;
- speed claim;
- feature claim.

Claims remain `unverified` until checked against an official source or reproducible run. Recommendations and engagement metrics never directly affect leaderboard scores.

## Workflow promotion

A recommended method becomes a workflow snapshot only when an evaluator can document:

1. required input;
2. every ordered step;
3. tool/model version used in each step;
4. prompts and settings;
5. human edits and decision points;
6. final output type;
7. cost and elapsed time.

If the post is unavailable or its key steps are ambiguous, keep it in the recommendation archive and request a transcript or screenshots. Do not infer missing steps.

## Evaluation

Run a workflow against the same task and artifact rubrics used for products, while adding:

- active human minutes;
- total elapsed minutes;
- number of tools/accounts;
- number of generation attempts;
- API/subscription cost;
- reproducibility between operators;
- intermediate artifact availability.

