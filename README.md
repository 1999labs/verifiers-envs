# Curator

> Look at a set of things and work out why they belong together, then find the ones that only look like they do.

**Tags:** `single-turn` `reasoning` `eval` `train` · **verifiers:** v1 (`verifiers.v1`)

**On the Hub:** [1999-labs/curator](https://app.primeintellect.ai/dashboard/environments/1999-labs/curator)

## What this is

Most reasoning environments test **answer-finding**. A question has a determinate
answer and the model's job is to reach it: solve the equation, find the fact,
pass the tests.

Curator tests something else. Someone shows you eight to twelve things and asks
you to say what they have in common. Then they ask which ones don't really
belong. There is no stated rule, and the two questions are coupled, because the
collection was built to make the second question depend on getting the first one
right.

Here is a real row from the dataset, verbatim:

```text
The collection:

A. Caesar salad: Romaine with croutons, parmesan, and a coddled-egg dressing.
B. Oysters Rockefeller: Baked oysters on the half shell under a rich green herb topping.
C. Bananas Foster: Bananas flambeed in butter, brown sugar, and rum, served over ice cream.
D. Chicken Marengo: Chicken braised with tomatoes, garlic, and wine, garnished with crayfish.
E. Pavlova: Meringue with a crisp crust and soft center, topped with fruit and cream.
F. Chicken Tetrazzini: Baked pasta and chicken in a creamy mushroom-and-sherry sauce.
G. Beef Stroganoff: Sauteed strips of beef in a sour-cream sauce.
H. Peach Melba: Poached peaches with raspberry sauce over vanilla ice cream.
I. Salisbury steak: Seasoned ground-beef patty served in brown gravy.
J. Carpaccio: Paper-thin slices of raw beef dressed with oil and shaved cheese.
K. Lobster Thermidor: Lobster in a cognac-cream sauce, returned to the shell and browned.
L. Nachos: Tortilla chips baked with melted cheese and sliced jalapenos.
```

The answer is `D` and `K`, because the principle is *dishes named after a
specific real person*. Chicken Marengo is named after the Battle of Marengo,
a village in Piedmont. It is tied to Napoleon but not named for him. Lobster
Thermidor is named after the play *Thermidor*, which is named after a month in
the French Revolutionary calendar. Nobody is involved.

Both intruders are real dishes with proper-noun names, so the obvious answer,
"restaurant dishes with capital letters in the name," explains all twelve items
and is wrong. The decoy is authored into every row on purpose.

The model has to do three things:

1. **Generate hypotheses over a set.** Propose candidate principles that explain
   most of the items.
2. **Discriminate between near-equivalent hypotheses.** The decoy explains
   *every* item, so the model has to find the tighter rule under which exactly
   one or two items fail.
3. **Use facts that are not in the text.** The principle usually turns on
   something about each item: where it came from, what it is made of, how it
   got its name. None of that appears in the description.

## Why I built it

I keep coming back to the judgment a curator or editor makes. Someone looks at a
shelf and sees why those things are on the same shelf. They notice the one that
was put there by mistake. That judgment is not retrieval and it is not
deduction. It is the ability to hold a lot of loose facts at once and notice
which ones bind.

That ability is what I want from the models I work with, and it is close to
absent from the Hub. The reward functions on these environments are almost all
built around convergent correctness, which makes them excellent at measuring
whether a model can find a known answer and poor at measuring whether it can
notice what is missing from a set.

There is a practical reason to want a signal like this measured now. Software
generation is getting cheap and fast. Generating a competent first draft of
almost anything is not going to stay scarce for long. Knowing what is worth
keeping, and being able to say why, is a different problem and I think it stays
valuable. If a training signal for that judgment is going to be built, it is
better built on purpose than stumbled into.

I want to be straight about what this environment is and is not. It is not a
benchmark of art criticism or a proxy for taste in any broad sense. It is a
narrow, mechanical version of one skill: over a set of short factual descriptions,
find the principle and the exceptions. Every row is hand-authored, every intruder
is documented, and the hard cases are hard because the decoy is good, not
because the question is vague.

## Why the signal is underrepresented

- **No keyword route.** Descriptions never contain the word for the property the
  principle is about. The dataset validator rejects any theme word that appears
  in member text but not intruder text. Shortcut solvers that pick the lexical
  odd-one-out or the description-length outlier score at or below random chance.
- **Intruders are adversarial by construction.** Every intruder is written to
  satisfy the decoy, and is usually the item people misremember as belonging.
  Ordinary odd-one-out puzzles do not do this.
- **Set-level, not item-level, judgment.** No single item can be judged alone.
  Whether "Tokyo Tower" is an intruder depends on whether the collection is about
  lattice towers or about structures built for world's fairs.
- **Graded, trainable reward.** Jaccard overlap on the intruder set gives dense
  partial credit, and the difficulty tiers spread the reward so the signal does
  not pile up at 0 or 1.

## Task format

The system prompt explains the task. The user message lists the collection above.
The reply must be exactly:

```text
<intruders>D, K</intruders>
<theme>Dishes named after a specific real person.</theme>
```

## Reward

| Signal | Weight | Definition |
|---|---|---|
| `intruders` | 0.7 | Jaccard overlap between the predicted and gold intruder ID sets. An exact set scores 1.0, partial overlap earns partial credit, a missing tag scores 0. |
| `theme` | 0.3 | An LLM judge grades the `<theme>` against the hidden principle: **A** same principle = 1.0, **B** partially right or too broad = 0.5, **C** wrong or just the decoy = 0.0. |

Metrics (not rewarded): `exact_match`, `format_ok`, and `judged` (1 if the judge ran).

**Graceful degradation.** The judge's key comes from `JudgeConfig.api_key_var`
(default `PRIME_API_KEY`, or the Prime CLI login). If no key resolves, the judge
is skipped and the `theme` slot mirrors the intruder score, so the total reward
equals the intruder Jaccard and still spans 0 to 1. The `judged` metric records
which mode ran. v1 has no `vf.ensure_keys`, so this check lives inside the reward
using the same key resolution the judge client uses.

## Dataset

The dataset is bundled at `curator/data/curator.jsonl` and uses Hugging
Face-compatible columns:

| Column | Content |
|---|---|
| `prompt` | Chat messages: `[system, user]` |
| `answer` | Sorted, comma-joined intruder IDs, e.g. `"D,K"` |
| `info` | `spec_id`, `theme`, `decoy`, `difficulty`, `domain`, `split`, and `items` (each with `id`, `title`, `description`, `is_intruder`, and `why` for intruders) |

**Size:** 203 rows, one per theme. 7 domains x 29 rows (design objects, music,
food, architecture, internet culture, tools, games).

| Tier | Rows | train / eval | 1 intruder / 2 intruders |
|---|---|---|---|
| obvious | 67 | 53 / 14 | 34 / 33 |
| moderate | 72 | 57 / 15 | 33 / 39 |
| subtle | 64 | 51 / 13 | 27 / 37 |

Collections hold 9 to 12 items. No item appears in more than one row. Validator
results on the full set:

| Check | Result |
|---|---|
| Theme-word leaks | 0 |
| Intruder position (first / middle / last third) | 0.31 / 0.38 / 0.32 |
| Random guess, told the true intruder count | 0.118 mean Jaccard |
| TF-IDF odd-one-out solver | 0.071 |
| Description-length outlier solver | 0.056 |

**Tiers**

- **obvious:** the principle is a familiar category, such as woodwinds or games
  with no element of chance. The intruder violates it in a way most people would
  see on reflection.
- **moderate:** the principle needs a specific fact about each item, such as
  whether it was built for a world's fair or began as a mod.
- **subtle:** the principle is second-order, such as dishes named after the
  person who actually invented them. The decoy explains every item, the intruders
  included.

**Splits.** `train` and `eval` are theme-disjoint: 20% of each tier is held out by
hashing `spec_id`. `split = "all"` (the default) uses everything.

### How it was generated

Each row comes from a hand-authored theme spec (`data_gen/specs/*.json`, rules in
`data_gen/AUTHORING.md`). A spec holds the principle, the decoy, 8 to 10 members,
and 1 to 3 near-miss intruders, each with a written `why`.

1. `data_gen/build_dataset.py` samples 8 to 12 items and one or two intruders per
   spec with a seeded RNG. It shuffles them, assigns letter IDs, and assigns splits.
2. `data_gen/validate_dataset.py` gates the result:
   - structural checks and near-duplicate theme detection
   - discriminative theme-word leaks
   - intruder-position balance
   - three shortcut baselines (random, TF-IDF odd-one-out, description-length
     outlier), which must not beat random
3. Every spec went through an adversarial fact-check pass. Members, intruders, and
   `why` claims had to be well documented and not time-sensitive. Anything
   uncertain was cut.

Rebuild after editing specs:

```bash
python data_gen/build_dataset.py data_gen/specs/*.json -o curator/data/curator.jsonl
python data_gen/validate_dataset.py curator/data/curator.jsonl
```

## Install

From the Hub:

```bash
prime env install 1999-labs/curator@latest
```

Or with uv, straight from the index:

```bash
uv pip install curator --extra-index-url https://hub.primeintellect.ai/1999-labs/curator/install/simple/
```

Or from source, in a checkout of this repository:

```bash
uv venv && uv pip install --prerelease=allow -e .
```

## Evaluate

Use the tool-less `null` harness, since the task is single-turn chat:

```bash
# quick smoke run
uv run vf-eval curator -m openai/gpt-4.1-mini -n 20 -r 3 --env.agent.harness.id null

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

`pyproject.toml` also carries `[tool.verifiers.eval]` defaults (30 examples x 3
rollouts) for tooling that reads them. v1 `vf-eval` reads the TOML config above.

To use the taskset directly in v1, construct it with its own config:

```python
from curator import CuratorTaskset
from curator.taskset import CuratorConfig

tasks = CuratorTaskset(CuratorConfig(split="eval", difficulty=["subtle"])).load()
```

## Tests

```bash
uv pip install pytest pytest-asyncio
uv run pytest
```

The tests cover dataset integrity, splits and filters, the validator, answer
parsing, Jaccard scoring (exact, partial, over-flagging, unformatted), the
no-key fallback, and the judge path with a mocked judge.

## The reward is non-degenerate

Claude Haiku 4.5 answered 90 puzzles blind (30 per tier, stratified sample,
seed 7). They were posed as the exact system and user prompts above, and the
answers were scored with this package's own `parse_intruders` and `jaccard`.
This is intruder reward only, which is the no-judge mode:

| Tier | Mean reward | Exact set | Scored 0 / partial / 1 |
|---|---|---|---|
| obvious | 0.572 | 40% | 7 / 11 / 12 |
| moderate | 0.328 | 27% | 18 / 4 / 8 |
| subtle | 0.150 | 7% | 23 / 5 / 2 |
| **overall** | **0.350** (sd 0.416) | 24% | 48 / 20 / 22 |

The reward falls monotonically with tier. It does not saturate at 0 or 1, and
within-tier variance is high, which is what GRPO-style training needs. Every reply
was well formatted. Subtle rows sit close to the 0.118 random floor for a small
model, which leaves headroom for stronger models and for training.

The container used to build this environment had no inference API access, so this
run went through a sandboxed subagent rather than `vf-eval`. `vf-eval` was
separately checked end to end, with the `null` harness and subprocess runtime,
against a local OpenAI-compatible stub. To reproduce with a real endpoint:

```bash
uv run vf-eval curator -m <model> -n 90 -r 1 --env.agent.harness.id null
```
