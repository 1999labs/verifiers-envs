"""Assemble curators-eye rows from hand-authored theme specs.

Each spec (data_gen/specs/*.json) is one hidden organizing principle with a pool
of members that satisfy it and a pool of near-miss intruders that share the
surface "decoy" theme but violate the principle. This script deterministically
(seeded by spec id) samples a collection of 8-12 items with one or two
intruders, shuffles it, assigns letter IDs, and writes HF-compatible rows:

    prompt  list[{"role", "content"}]  system + user messages
    answer  str                        sorted, comma-joined intruder IDs ("C,H")
    info    dict                       theme, decoy, tier, domain, split, items (with truth)

Usage:
    python data_gen/build_dataset.py data_gen/specs/*.json -o curators_eye/data/curators_eye.jsonl
"""

import argparse
import hashlib
import json
import random
import string
from pathlib import Path

SYSTEM_PROMPT = """\
You are a curator reviewing a collection. Every item was chosen according to a \
single organizing principle, which is never stated. One or two items are \
intruders: they look like they belong, but they violate the principle.

Identify the intruder(s) and name the organizing principle. Respond in exactly \
this format:
<intruders>comma-separated item IDs</intruders>
<theme>one sentence stating the organizing principle</theme>"""

MIN_ITEMS, MAX_ITEMS = 8, 12


def rng_for(spec_id: str) -> random.Random:
    return random.Random(int(hashlib.sha256(spec_id.encode()).hexdigest()[:16], 16))


def build_row(spec: dict) -> dict:
    rng = rng_for(spec["id"])
    intruders = list(spec["intruders"])
    # Spec intruder pools may hold more than two candidates; use one or two of them.
    n_intruders = min(len(intruders), rng.choice([1, 2]) if len(intruders) > 1 else 1)
    intruders = rng.sample(intruders, n_intruders)
    n_members = min(len(spec["members"]), MAX_ITEMS - n_intruders)
    if n_members + n_intruders < MIN_ITEMS:
        raise ValueError(f"{spec['id']}: only {n_members + n_intruders} items")
    members = rng.sample(spec["members"], n_members)

    items = [{**m, "is_intruder": False} for m in members] + [
        {**i, "is_intruder": True} for i in intruders
    ]
    rng.shuffle(items)
    # Move the first intruder into a randomly chosen third of the list, so intruder
    # positions stay balanced across the dataset and position bias can't be exploited.
    n = len(items)
    third = rng.randrange(3)
    target = rng.randrange(third * n // 3, (third + 1) * n // 3)
    first = next(i for i, it in enumerate(items) if it["is_intruder"])
    items[first], items[target] = items[target], items[first]
    for letter, item in zip(string.ascii_uppercase, items):
        item["id"] = letter

    listing = "\n".join(f"{it['id']}. {it['title']}: {it['description']}" for it in items)
    answer = ",".join(sorted(it["id"] for it in items if it["is_intruder"]))
    return {
        "prompt": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"The collection:\n\n{listing}"},
        ],
        "answer": answer,
        "info": {
            "spec_id": spec["id"],
            "theme": spec["theme"],
            "decoy": spec["decoy"],
            "difficulty": spec["tier"],
            "domain": spec["domain"],
            "items": [
                {
                    "id": it["id"],
                    "title": it["title"],
                    "description": it["description"],
                    "is_intruder": it["is_intruder"],
                    "why": it.get("why", ""),
                }
                for it in items
            ],
        },
    }


def assign_splits(rows: list[dict], eval_every: int = 5) -> None:
    """Theme-disjoint split: within each tier, every `eval_every`-th row (in a
    hash-shuffled order) is held out as `eval`, the rest are `train`."""
    for tier in {r["info"]["difficulty"] for r in rows}:
        tier_rows = [r for r in rows if r["info"]["difficulty"] == tier]
        tier_rows.sort(key=lambda r: hashlib.sha256(r["info"]["spec_id"].encode()).hexdigest())
        for i, row in enumerate(tier_rows):
            row["info"]["split"] = "eval" if i % eval_every == 0 else "train"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("specs", nargs="+", type=Path)
    parser.add_argument("-o", "--out", type=Path, required=True)
    args = parser.parse_args()

    specs = [s for path in sorted(args.specs) for s in json.loads(path.read_text())]
    ids = [s["id"] for s in specs]
    if dupes := {i for i in ids if ids.count(i) > 1}:
        raise SystemExit(f"duplicate spec ids: {sorted(dupes)}")
    rows = [build_row(s) for s in sorted(specs, key=lambda s: s["id"])]
    assign_splits(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    print(f"wrote {len(rows)} rows -> {args.out}")


if __name__ == "__main__":
    main()
