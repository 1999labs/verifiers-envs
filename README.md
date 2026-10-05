# curators-eye

> Find the near-miss intruders in a curated collection, then name the rule the curator never stated.

**Tags:** `single-turn` `reasoning` `eval` `train` · **verifiers:** v1 (`verifiers.v1`)

## Thesis

Most reasoning environments on the Hub test **answer-finding**. A question has a
determinate answer, and the model's job is to reach it: solve the equation, find
the fact, pass the tests. This environment tests something different.
**Perception of unstated organizing principles** is the judgment a curator,
editor, or good reviewer exercises when they look at a set of things and see
*why these belong together*, and which ones only look like they do.

Each task shows 8–12 items (a title and a one-line description) chosen by a
hidden principle. One or two are **near-miss intruders**: they share a strong
surface theme (the *decoy*) with the real members but break the tighter
principle. Example:

| | Item | |
|---|---|---|
| | Peach Melba, Pavlova, Beef Stroganoff, Carpaccio, Nachos, Caesar salad, … | members: dishes named after a real person |
| ✗ | **Chicken Marengo** | named after a battle, though tied to Napoleon |
| ✗ | **Lobster Thermidor** | named after a play, and it sounds like a surname |

Solving this requires three things:

1. **Hypothesis generation over sets.** Propose candidate principles that
   explain most of the items.
2. **Discrimination between near-equivalent hypotheses.** The decoy explains
   *every* item, so the model has to find the tighter rule under which exactly
   one or two items fail.
3. **Grounded knowledge.** The principle usually depends on facts about each item
   (origin, mechanism, material, naming history) that never appear in the text.

### Why this signal is underrepresented

- **No keyword route.** Descriptions never mention the property the principle is
  about. The dataset validator rejects any theme word that appears in member text
  but not intruder text. Shortcut solvers that pick the lexical odd-one-out or
  the description-length outlier score *at or below random chance*.
- **Intruders are adversarial by construction.** Every intruder is authored to
  satisfy the decoy, and is usually the item people misremember as belonging.
  Typical odd-one-out puzzles don't do this.
- **Set-level, not item-level, judgment.** No single item can be judged in
  isolation. Whether "Tokyo Tower" is an intruder depends on whether the
  collection is about *lattice towers* or *structures built for world's fairs*.
- **Graded, trainable reward.** Jaccard overlap on the intruder set gives dense
  partial credit. Difficulty tiers spread the reward so the signal doesn't
  saturate at 0 or 1.

Today the Hub mostly measures convergent correctness. This environment measures
the taste-adjacent skill of seeing structure nobody pointed out, which is closer
to what we want from models acting as editors, reviewers, and research
assistants.

## Task format

The system prompt explains the task. The user message lists the collection:

```text
The collection:

A. Oware: Seeds are sown around a ring of pits, capturing on certain counts.
B. Abalone: Marbles shove each other off the edge of a hexagonal board.
...
```

The model must answer:

```text
<intruders>E, G</intruders>
<theme>Games with no element of chance: outcomes depend only on player decisions.</theme>
```

## Reward

| Signal | Weight | Definition |
|---|---|---|
| `intruders` | 0.7 | Jaccard overlap between the predicted and gold intruder ID sets. An exact set scores 1.0. Partial overlap earns partial credit. A missing tag scores 0. |
| `theme` | 0.3 | An LLM judge grades the `<theme>` against the hidden principle: **A** same principle = 1.0, **B** partially right or too broad = 0.5, **C** wrong or just the decoy = 0.0. |

Metrics (not rewarded): `exact_match`, `format_ok`, and `judged` (1 if the judge ran).

**Graceful degradation.** The judge's key comes from `JudgeConfig.api_key_var`
(default `PRIME_API_KEY`, or the Prime CLI login). If no key resolves, the judge
is skipped and the `theme` slot mirrors the intruder score. The total reward
then equals the intruder Jaccard and still spans 0–1. The `judged` metric
records which mode ran. v1 has no `vf.ensure_keys`, so this check lives inside
the reward using the same key resolution the judge client uses.

## Dataset

The dataset is bundled at `curators_eye/data/curators_eye.jsonl` and uses
Hugging Face-compatible columns:

| Column | Content |
|---|---|
| `prompt` | Chat messages: `[system, user]` |
| `answer` | Sorted, comma-joined intruder IDs, e.g. `"C,K"` |
| `info` | `spec_id`, `theme`, `decoy`, `difficulty`, `domain`, `split`, and `items` (each with `id`, `title`, `description`, `is_intruder`, and `why` for intruders) |

**Size:** 203 rows, one per theme. 7 domains × 29 rows (design objects, music,
food, architecture, internet culture, tools, games).

| Tier | Rows | train / eval | 1 intruder / 2 intruders |
|---|---|---|---|
| obvious | 67 | 53 / 14 | 34 / 33 |
| moderate | 72 | 57 / 15 | 33 / 39 |
| subtle | 64 | 51 / 13 | 27 / 37 |

Collections hold 9–12 items. No item appears in more than one row. Validator
results on the full set:

| Check | Result |
|---|---|
| Theme-word leaks | 0 |
| Intruder position (first / middle / last third) | 0.31 / 0.38 / 0.32 |
| Random guess, told the true intruder count | 0.118 mean Jaccard |
| TF-IDF odd-one-out solver | 0.071 |
| Description-length outlier solver | 0.056 |


**Tiers**

- **obvious:** the principle is a familiar category (woodwinds, zero-chance
  games). The intruder violates it in a way most people would see on reflection.
- **moderate:** the principle needs a specific fact about each item (built for
  a world's fair, began as a mod).
- **subtle:** the principle is second-order (named after the person who
  *actually* invented it). The decoy explains every item, including the
  intruders.

**Splits.** `train` and `eval` are theme-disjoint: 20% of each tier is held out
by hashing `spec_id`. `split = "all"` (the default) uses everything.

### How it was generated

Each row comes from a hand-authored theme spec (`data_gen/specs/*.json`, rules in
`data_gen/AUTHORING.md`). A spec holds the principle, the decoy, 8–10 members,
and 1–3 near-miss intruders, each with a written `why`.

1. `data_gen/build_dataset.py` samples 8–12 items and one or two intruders per
   spec with a seeded RNG. It shuffles them, assigns letter IDs, and assigns
   splits.
2. `data_gen/validate_dataset.py` gates the result:
   - structural checks and near-duplicate theme detection
   - discriminative theme-word leaks
   - intruder-position balance
   - three shortcut baselines (random, TF-IDF odd-one-out, description-length
     outlier), which must not beat random
3. Every spec went through an adversarial fact-check pass. Members, intruders and
   `why` claims had to be well documented and not time-sensitive. Anything
   uncertain was cut.

Rebuild after editing specs:

```bash
python data_gen/build_dataset.py data_gen/specs/*.json -o curators_eye/data/curators_eye.jsonl
python data_gen/validate_dataset.py curators_eye/data/curators_eye.jsonl
```

## Install

```bash
# from the Hub
prime env install <owner>/curators-eye

# or from source (from the repo root)
uv venv && uv pip install --prerelease=allow -e .
```

## Evaluate

Use the tool-less `null` harness, since the task is single-turn chat:

```bash
# quick smoke run
uv run vf-eval curators-eye -m openai/gpt-4.1-mini -n 20 -r 3 --env.agent.harness.id null

# the bundled config: 30 held-out tasks x 3 rollouts
uv run vf-eval @ configs/eval.toml

# useful overrides
--env.taskset.split eval                  # train | eval | all
--env.taskset.difficulty '["subtle"]'     # filter tiers
--env.taskset.task.judge.model openai/gpt-4.1-mini
--env.taskset.task.judge.api-key-var OPENAI_API_KEY
--env.taskset.task.judge.base-url https://api.openai.com/v1
--env.agent.runtime.type subprocess       # run locally without a Prime tunnel
```

`pyproject.toml` also carries `[tool.verifiers.eval]` defaults (30 examples × 3
rollouts) for tooling that reads them. v1 `vf-eval` reads the TOML config above.

## Tests

```bash
uv pip install pytest pytest-asyncio
uv run pytest
```

The tests cover dataset integrity, splits and filters, the validator, answer
parsing, Jaccard scoring (exact, partial, over-flagging, unformatted), the
no-key fallback, and the judge path with a mocked judge.

## Reward is non-degenerate: small-model run

Claude Haiku 4.5 answered 90 puzzles blind (30 per tier, stratified sample,
seed 7). They were posed as the exact system and user prompts above, and the
answers were scored with this package's own `parse_intruders` and `jaccard`.
This is intruder reward only (the no-judge mode):

| Tier | Mean reward | Exact set | Scored 0 / partial / 1 |
|---|---|---|---|
| obvious | 0.572 | 40% | 7 / 11 / 12 |
| moderate | 0.328 | 27% | 18 / 4 / 8 |
| subtle | 0.150 | 7% | 23 / 5 / 2 |
| **overall** | **0.350** (sd 0.416) | 24% | 48 / 20 / 22 |

The reward falls monotonically with tier. It doesn't saturate at 0 or 1, and
within-tier variance is high, which is what GRPO-style training needs. Every
reply was well formatted. Subtle rows sit close to the 0.118 random floor for a
small model, which leaves headroom for stronger models and for training.

The container used to build this environment had no inference API access, so
this run went through a sandboxed subagent rather than `vf-eval`. `vf-eval` was
separately checked end to end, with the `null` harness and subprocess runtime,
against a local OpenAI-compatible stub. To reproduce with a real endpoint:

```bash
uv run vf-eval curators-eye -m <model> -n 90 -r 1 --env.agent.harness.id null
```

