# SciFact data and attribution

Download SciFact from the official [AllenAI SciFact repository](https://github.com/allenai/scifact) using its documented release. Extract it locally under this directory so the files are available beneath data/scifact.

The official SciFact license distinguishes the materials:

- Claims and evidence annotations (claims_*.jsonl): CC BY 4.0.
- Abstract corpus (corpus.jsonl): part of Semantic Scholar S2ORC and licensed ODC-By 1.0.
- SciFact repository code: Apache 2.0.

This project does not bundle the benchmark archive or corpus text. The data folder is ignored by Git to avoid accidentally committing the licensed corpus. Keep the original license and attribution with any local copy, and review the upstream terms before publishing derived data or results.

Suggested citation: Wadden et al., “Fact or Fiction: Verifying Scientific Claims,” EMNLP 2020.
