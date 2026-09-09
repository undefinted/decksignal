# Related work and positioning

OpenPPTBench builds on, and should remain interoperable with, existing presentation benchmarks:

- [SlidesGen-Bench](https://github.com/YunqiaoYang/SlidesGen-Bench) evaluates content fidelity, visual aesthetics, and editability across generation paradigms.
- [DECKBench](https://github.com/morgan-heisler/DeckBench) covers academic paper-to-slide generation and multi-turn editing.
- [PPTC](https://github.com/gydpku/PPTC) evaluates model performance on slide creation and template editing tasks.
- [Gloss](https://github.com/aronchick/gloss) checks whether native presentation artifacts both look right and are structurally correct.
- [PresentBench](https://arxiv.org/abs/2603.07244) uses instance-specific binary rubrics for fine-grained factual and requirement coverage.
- [PPTBench](https://arxiv.org/abs/2512.02624) covers detection, understanding, modification, and generation with layout-centric samples.
- [PPTArena](https://github.com/michaelofengenden/PPTArena) targets in-place edits to text, charts, tables, animations, and master styles.
- [SlideBench](https://www.slidebench.org/methodology) separates artifact quality from PPTX malleability and reports category-scoped results.

OpenPPTBench v0.1 differentiates itself through realistic Chinese-language tasks, evaluation of end-user products as well as developer systems, versioned run records, and community-facing blinded comparisons. Where an established metric or data format can be reused, compatibility is preferred over reinvention.
