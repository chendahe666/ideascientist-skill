---
name: ideascientist
description: Generate literature-grounded research proposals using IdeaScientist gap finding, cross-setting mechanism transfer, and proposal writing; inspect or reproduce its paper, code, training, and evaluation. Use for IdeaScientist requests or an explicit research problem and challenge that needs a sourced, testable proposal.
---

# IdeaScientist

Turn an explicit research problem and challenge into a proposal whose gap, source mechanism, transfer assumptions, and experimental predictions can be inspected. Respond in the user's language; default to Chinese when the request is in Chinese.

This is an independent skill adaptation of **IdeaScientist: Orchestrating Agents for Grounded Scientific Ideation**, arXiv **2610.04074v1**, with a bundled paper and unmodified upstream source snapshot. The adapted workflow uses the host agent and available retrieval tools. It does **not** supply trained role adapters or reproduce the paper's scores merely by running prompts. Read [sources.md](references/sources.md) for attribution and pinned sources.

## Choose the requested work

- **Generate a proposal:** use the workflow below. Read [workflow.md](references/workflow.md) for role contracts and output schemas.
- **Explain the paper or inspect evidence:** read [paper.md](references/paper.md) and [evaluation.md](references/evaluation.md), then consult the original at the stated section/table. Distinguish paper facts, code behavior, and your interpretation.
- **Run upstream inference, evaluation, or training:** first read [reproduction.md](references/reproduction.md). Verify local source hashes with `python scripts/prepare_upstream.py`. Extract with `--extract-to <new-directory>` only when needed. Inspect prerequisites and the actual requested command before installing dependencies or starting a model/job. A request for this skill alone does not authorize paid APIs, GPU rentals, or full training.

Resolve script and reference paths relative to this skill folder. Write research outputs into a separate user workspace run directory.

## Proposal workflow

### Establish the input

Record the task's concrete input, desired output, existing-method challenge, and resource constraints. Infer routine details from the conversation. If the challenge itself is uncertain, mark it as a hypothesis and make its verification the first experiment. If the user only supplies a broad area, identify candidate problems with sources before treating one as established; the original paper assumes a supplied problem and challenge.

Initialize the record when useful:

```text
python scripts/init_run.py --run-dir <new-run-directory> --problem "<input and desired output>" --challenge "<specific failure or constraint>"
```

This creates pending artifacts, not a completed research result. Use `--help` for mode and cutoff options. A cutoff is optional for ordinary research; it is required for a claimed temporal reproduction. Mark the default mode `adapted` and record the model/tools actually used.

### Ground the gap

Find the closest existing methods for the same task and challenge. Read the relevant original text or code before asserting a limitation. Record each source URL/version, exact section/equation/table/code locator, what was read, and which claim it supports in `evidence.json`.

For each gap, name the near-miss work and explain precisely why its mechanism falls short under the stated condition. Prefer a small number of well-supported gaps. Search absence, abstract-only reading, and a paper's own future-work sentence alone do not establish a field-wide gap. Record counterevidence and unresolved access limits.

### Find and adapt a mechanism

Look for a different problem setting with the same underlying obstacle. As a starting strategy, search several neighboring subfields using the challenge rather than only the target field's vocabulary. This query strategy is adapted from the paper; it is not a requirement to exhaust a fixed number of searches.

For each candidate, make the chain explicit:

1. The source setting and concrete mechanism, with a read source.
2. The shared structure between source and target.
3. The change needed to make the mechanism operate in the target.
4. The transfer assumption and main reason it might fail.
5. The closest target-domain method and the substantive difference.

Treat analogy as a hypothesis until tested. Establish conceptual feasibility before spending effort on attack experiments. Use a reviewer or independent context when it would help resolve a consequential uncertainty; preserve its evidence and verdict rather than treating a score as authority. If no candidate is supported, report that result.

### Write the surviving proposal

Complete `report.json` with the selected mechanism, problem definition, method, closest-work comparison, implementation details needed at this stage, limitations, and falsifiable predictions. Complete `experiment_plan.json` with datasets, baselines, metrics, controls, budget, success criteria, and stop rules. Keep proposed improvements separate from measured outcomes.

When transfer is the central claim, compare the target baseline **A**, direct transfer **B**, and, if an adaptation is proposed, **B + adaptation** under matched conditions. These comparisons are this skill's practical extension, not an experiment performed in the IdeaScientist paper. If a different design better answers the user's question, document the reason and adapt the plan.

Keep separate conclusions for: the target problem exists; the proposed explanation is supported; direct transfer works; adaptation adds value. The next action should be the smallest experiment that resolves the most important uncertainty.

### Check and deliver

```text
python scripts/validate_run.py <run-directory>
```

The checker verifies structure and declared provenance only. It cannot confirm that a URL was actually read, a cited passage entails a claim, a method is novel, or an experiment will succeed. Fill reading status honestly and inspect the underlying evidence. A structural pass retains `empirical_status: untested`.

Deliver the proposal, source mechanisms, nearest-work differences, key uncertainty, and next decisive experiment. Include source links and clearly label any illustrative or synthetic material. Do not call a promising proposal, reviewer preference, or checker pass a validated scientific contribution.

## Reproduction boundaries

- Preserve the difference between **adapted agent workflow**, **upstream untrained harness**, and **upstream trained system** in every result.
- The paper's headline +14.0 is a score-point difference; training contributes +1.1 overall points relative to the untrained harness in Table 1.
- In-domain novelty is a binary structural-transfer judgment. It is not a general literature novelty certificate.
- The public dataset's counts and public training/evaluation code differ from the paper in documented ways. Follow [reproduction.md](references/reproduction.md) before claiming a matched reproduction.
- A retrieval cutoff does not prove the model's parameters lack later knowledge. Log model identity, corpus revision, cutoff, prompts, budgets, failed runs, and any deviations.

## Bundled resources

- `assets/sources/paper-2610.04074v1.pdf`: original paper, CC BY 4.0.
- `assets/sources/upstream-code.zip`: unmodified upstream commit `82a98a08772eab08d11fd097445afa4a8eaaa5b3`, CC BY-NC 4.0.
- `assets/sources/dataset-card.md`: pinned dataset description; the multi-gigabyte dataset and model weights are not bundled.
- `assets/sources/manifest.json`: source URLs, revisions, sizes, and SHA-256 hashes.
- `scripts/init_run.py`, `validate_run.py`: offline scaffolding and structural checks.
- `scripts/prepare_upstream.py`: offline hash verification and safe source extraction.
