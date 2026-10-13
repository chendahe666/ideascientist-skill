# Adapted workflow and research record

This document describes the **skill adaptation**, not a literal copy of upstream prompts or an empirical replication. The original role contracts and output fields are summarized in `paper.md`; this record adds explicit provenance and an experiment handoff for ordinary research use.

## Inputs and modes

Use `init_run.py --help` for the command interface. It accepts a concrete problem, challenge, new run directory, optional retrieval cutoff, and a mode of `adapted` or `upstream`. The mode records intended execution; it does not automatically invoke an upstream model.

- `adapted`: the current host agent uses the role contracts with its actual available tools. Record the actual model/tool identities in `input.json` and the run plan.
- `upstream`: inspect the pinned source and `reproduction.md`, prepare the actual database, index and endpoint, then run upstream commands under the user's authorized resources. Keep upstream logs separate from adapted record files. Initializing the record does not run upstream code.

A broad topic is not yet the original paper's problem-plus-challenge input. When the problem is uncertain, use evidence collection to formulate it and mark its existence as an assumption to check.

## The handoffs

| Role | Reads | Produces | Reviewer question |
|---|---|---|---|
| Gap finder | Problem, challenge, closest methods | Gap and specific near misses | Is this a real mechanism-level limitation in this setting? |
| Innovator | Gap, sources from analogous settings | Transferable mechanism and its assumptions | What shared structure makes this transfer plausible? |
| Report writer | Supported gap and surviving candidate | Implementable proposal and predictions | Is the proposed mechanism sufficiently specified to test? |
| Experiment planner, an extension | Proposal and resource constraints | Smallest decisive experiment | Which result would change the decision to pursue this idea? |

Use independent contexts or subagents when useful. Do not imply that assigning roles trained the host model. Preserve rejected candidates and their reasons in the record or plan.

## Files created by the initializer

The scripts use `schema_version: "1.0"`. The initializer emits `status: "pending"`; set a stage to `complete` only after filling and checking its contents. Inspect the generated JSON for the authoritative field names.

| File | What to record |
|---|---|
| `input.json` | Problem, challenge, mode, optional cutoff and available resources |
| `plan.md` | Current stage, assumptions, decisions, blockers and next action |
| `evidence.json` | Actually read sources, exact locators and supported claims |
| `gaps.json` | Specific limitation, supporting evidence and near-miss papers |
| `candidates.json` | Source mechanism, shared structure, adaptation, assumption, risk and closest-work difference |
| `report.json` | Selected candidate, concrete method, limitations and falsifiable predictions |
| `experiment_plan.json` | Baselines, metrics, controls, compute/data budget, success criteria and stop rules |

### Provenance

Every paper has a stable local `id`, title, original `url`, `read_status`, and a nonempty list of claims with `text`, `locator`, and `source_url`. Use `read_status: "read"` only for material actually accessed. A search snippet or unread citation is not a full-text reading. Indicate the scope in the locator, for example `Section 3.2, reward equation`, `Table 1`, or `repo@commit:path:L25`.

Artifacts use `evidence_ids` that resolve to these local IDs. Gap `near_misses` entries contain `{paper_id, why_insufficient}`. Candidate `closest_work` is a list of paper IDs; its `difference` string explains the mechanism-level distinction. The record is a declaration of provenance; the structural checker cannot independently inspect a webpage or establish entailment.

Do not cite a reference that was inaccessible as support for a specific mechanism. Keep its status as unresolved and qualify the claim. For temporally controlled work, preserve publication dates and versions and prevent later sources reaching proposal generation; later literature may be available to a separate evaluator.

### Transfer candidate

Each candidate should identify the gap it targets, the source mechanism, shared structure, target adaptation, transfer assumption, main risk, evidence IDs, and the closest target work with a concrete difference. Avoid replacing the mechanism with a technology name such as "use a transformer".

Keep conceptual plausibility and empirical support separate. State why the source mechanism worked in its original setting using source evidence. Then explain what is still a hypothesis in the target setting. Do not claim success simply because the two settings share a vocabulary.

### Proposal and experiment plan

Select one candidate in the report. Include enough implementation detail to expose the key assumption and permit a small test. Predictions should specify the observation that would contradict them. Never invent measured performance numbers to fill a proposal schema.

For a transfer claim, the default experiment plan contains:

- `baseline`: the target-domain method A.
- `direct_transfer`: the imported source mechanism B, with only required interface changes.
- `adapted`: B plus the proposed scientific adaptation, when applicable.

Match data splits, model/backbone, training and inference budget, and evaluation conditions where the comparison requires it. Record planned metrics, success thresholds, stop rules, and why an omitted arm is inapplicable. If only a problem-existence probe is justified, state that the transfer/adaptation stages remain deferred; do not fill them with fictitious methods merely to satisfy a checker.

The helper validator intentionally implements a narrow three-variant plan. If an authorized study needs a different design, retain a separate explicit protocol and note that this helper's structural pass does not cover it rather than bending the science to fit a template.

## What a checker pass means

Run `python scripts/validate_run.py <run-directory>`. An empty scaffold is expected to fail. The checker detects missing fields, unresolved or declared-unread citations, absent transfer terms, and incomplete experiment controls. It reports `validation_scope: structural_only` and `empirical_status: untested`.

It does not prove a cited source is real or was read, an interpretation is correct, a proposal is novel, a predicted result will occur, or a scientific claim is supported. Check those through source reading and appropriate experiments. Treat the synthetic test fixture as a software test only.
