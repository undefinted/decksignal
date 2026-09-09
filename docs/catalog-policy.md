# Method catalog policy

The catalog tracks reproducible ways to make presentations, not every social post as a separate item. Multiple posts describing the same tool chain are merged into one workflow and retained as source references.

## Evidence states

- `discovered`: a source mentions the method, but its exact steps or dependencies are incomplete.
- `documented`: the main steps can be reconstructed from accessible sources.
- `queued`: the method has been selected for a common benchmark run.
- `evaluated`: artifacts, costs, timing, and review evidence from that run are available.
- `stale`: a previously usable method may no longer match the current product.
- `archived`: retained for history but no longer considered an active option.

Creator claims such as “one minute,” “fully editable,” or “ten times faster” are never converted into benchmark scores. Product capabilities taken from official pages remain vendor claims until a dated run verifies them.

## Discovery coverage

Seed discovery covers Xiaohongshu, Bilibili, YouTube, GitHub, official documentation, and web tutorials. Platform search results are incomplete and personalized, so the project does not claim exhaustive coverage. New sources can be proposed with the repository's **New method** issue form; maintainers normalize and deduplicate accepted submissions before testing.

## Deduplication rule

Two sources belong to the same workflow when their essential input, transformation stages, tool chain, and output format are equivalent. Variants remain separate when they change a material constraint, such as native PPTX versus image-only output, local versus hosted execution, or single-tool versus multi-tool production.
