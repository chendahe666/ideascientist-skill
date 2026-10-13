# Attribution and modifications

This independent skill package is based on:

**Jiarui Liu et al. (2026). IdeaScientist: Orchestrating Agents for Grounded Scientific Ideation. arXiv:2610.04074v1.**

- Paper: https://arxiv.org/abs/2610.04074v1
- Authors and affiliations: https://arxiv.org/html/2610.04074v1
- Code: https://github.com/jiarui-liu/IdeaScientist
- Dataset: https://huggingface.co/datasets/Jerry999/SvalbardIdeaVault

The authors retain ownership of their original work. This package is not endorsed by Meta, Carnegie Mellon University, the other affiliated institutions, or the original authors.

## Original material

- The paper PDF is redistributed unmodified under **CC BY 4.0**: https://creativecommons.org/licenses/by/4.0/ .
- The code ZIP is an unmodified source archive at commit `82a98a08772eab08d11fd097445afa4a8eaaa5b3`, under **CC BY-NC 4.0**. The upstream license is preserved inside the archive and at `skills/ideascientist/assets/sources/upstream-LICENSE`.
- The upstream README is preserved unmodified beside the archive under the upstream license.
- The dataset card is preserved at revision `64ab36be959afab06066f8c1e7ea292dba9362e5`, under the dataset's stated **CC BY 4.0** license. The dataset itself is not redistributed here.

## Adaptations in this package

The Chinese explanations, SKILL.md, research-record schemas, host-agent workflow, structural validator, safe extraction helper, and packaging checks are new adaptations. The host-agent workflow is not a trained model checkpoint, and the practical baseline/direct-transfer/adaptation experiment plan is an extension rather than a result reported by the original paper. Condensed or adapted instructions are not labeled as verbatim upstream prompts.

These additions are licensed under **CC BY-NC 4.0**. They make no empirical claim about IdeaScientist performance. Commercial use of the upstream code or these additions requires permission consistent with the applicable license.

Full legal code: https://creativecommons.org/licenses/by-nc/4.0/legalcode
