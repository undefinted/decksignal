# Continuous evaluation observatory

## Product definition

OpenPPTBench is a meta-evaluation and market-observation system. It answers four questions:

1. Which AI presentation products currently exist, and what changed recently?
2. Which capabilities has each product actually been tested on?
3. What do independent benchmarks, local reproducible runs, experts, and users each conclude?
4. Which product is best for a specific user, scenario, language, and output requirement today?

The system must not imply that scores from unrelated benchmarks are directly comparable.

## System layers

```text
Official sites / release notes / repositories / community submissions
                              |
                    discovery and verification
                              |
                     versioned tool registry
                              |
        +---------------------+---------------------+
        |                     |                     |
 imported benchmarks   reproducible local runs   blind human votes
        |                     |                     |
        +---------------- normalized evidence records ---------------+
                                      |
                         capability ontology mapping
                                      |
                     score + coverage + confidence + age
                                      |
                    scenario leaderboards and comparisons
```

## 1. Discovery and verification

Discovery produces candidates, not facts. A candidate can originate from an official release, repository, app marketplace, product submission, or community report. Before appearing as a verified product, an editor or automated verifier confirms its canonical URL, provider, availability, output modes, and last-seen date.

Product facts must carry field-level provenance. Price, free limits, export formats, and model versions change independently and should not share one blanket `verified_at` value.

Suggested states:

- `discovered`: unverified candidate;
- `verified`: official source checked;
- `queued`: ready for evaluation;
- `evaluated`: has current evidence;
- `stale`: latest qualifying evidence exceeds its freshness window;
- `unavailable`: product is no longer usable;
- `archived`: retained only for historical comparison.

## 2. Benchmark adapters

An adapter does not rewrite another benchmark. It records the upstream version, executes the official evaluator where possible, captures raw outputs, and maps only supported metrics to the common capability ontology.

Initial adapter targets:

- SlidesGen-Bench: content fidelity, visual aesthetics, editability;
- PresentBench: instance-specific grounded checks;
- Gloss: native artifact correctness and editability;
- DECKBench: academic document-to-deck and multi-turn editing;
- PPTC/PPTArena/PPTBench: agentic creation, editing, and layout understanding.

Every mapping is explicit and reviewable. Unmapped upstream metrics remain visible in their native form.

## 3. Common capability ontology

The normalized model uses capabilities rather than benchmark names:

| Capability | Examples of evidence |
|---|---|
| content_grounding | factual retention, unsupported claims, source coverage |
| narrative_structure | storyline, prioritization, slide roles, conclusion quality |
| visual_design | hierarchy, layout, typography, image relevance |
| instruction_following | language, audience, page count, required elements |
| native_editability | editable text/charts, grouping, masters, non-flattened output |
| export_fidelity | PPTX/PDF rendering, font substitution, corruption, clipping |
| generation_reliability | success rate, latency, retries, deterministic failures |
| editing_capability | localized edits, style preservation, multi-turn consistency |
| usability | workflow friction, required choices, correction effort |
| accessibility | contrast, reading order, alt text, projection readability |
| localization_zh | Chinese typography, punctuation, line breaking, business phrasing |
| value | price, free limits, watermarks, usable output per unit cost |

Scores are reported per capability and per scenario. Missing capabilities remain missing; they are never filled with a neutral value.

## 4. Evidence hierarchy

Evidence type affects confidence, not the observed score itself.

| Evidence | Default confidence class |
|---|---|
| Reproducible run using an official benchmark and preserved artifact | A |
| Reproducible OpenPPTBench run with complete manifest | A |
| Independent benchmark result with available artifacts but no local rerun | B |
| Blinded human comparison with quality controls | B |
| Expert review with disclosed rubric and reviewer role | B |
| Vendor claim or product demo | D; discovery only |
| Anonymous anecdote | D; discovery only |

Vendor claims and anonymous anecdotes must not directly affect leaderboard scores.

## 5. Ranking outputs

There is no single default global winner. Public ranking views include:

- prompt-to-deck;
- document-to-deck;
- deck editing;
- Chinese-language business decks;
- education decks;
- best native PPTX;
- best free option;
- fastest reliable first draft;
- human preference arena;
- open-source systems.

An optional overall index is permitted only for products exceeding a published minimum coverage threshold.

## 6. Update loop

1. Discover or receive a candidate/product change.
2. Verify official facts and create a version snapshot.
3. Determine which evidence is now stale or invalidated.
4. Schedule a small smoke task.
5. If behavior materially changed, schedule the full relevant suite.
6. Run adapters and local tests; preserve artifacts and logs.
7. Queue blinded review where machine metrics are insufficient.
8. Recompute scenario rankings and publish a changelog.

## 7. Public website

Minimum pages:

- `/tools`: verified registry with freshness indicators;
- `/leaderboards`: scenario-specific rankings with confidence intervals;
- `/compare`: same task and same date-range comparison;
- `/tools/{id}`: version timeline, evidence, capabilities, pricing snapshots;
- `/arena`: randomized blind A/B review;
- `/methodology`: mappings, weights, exclusions, conflicts, and limitations;
- `/changes`: newly discovered tools and material ranking changes.

Every displayed score should link back to the evidence records that produced it.

