"""Quality gates for a built curators-eye JSONL file.

Hard failures (exit 1): malformed rows, item counts outside 8-12, intruder counts
outside 1-2, duplicate items within a row, duplicate themes across rows, invisible
characters (e.g. emoji variation selectors) that could act as hidden cues.

Reported diagnostics (should stay low; investigate outliers):
  * theme-word leak: a word of the hidden theme that appears in member text but in
    no intruder's text (so it could point at the principle and away from intruders)
  * intruder position balance across first/middle/last thirds (error if skewed)
  * shortcut baselines, each told the true intruder count (a generous oracle-k):
      - random:  expected Jaccard of a random k-subset
      - lexical: TF-IDF odd-one-out (least similar items to the rest)
      - length:  items whose description length is furthest from the row median
    Any shortcut scoring well above random means intruders are detectable without
    understanding the principle, so the row should be rewritten.
"""

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

INVISIBLE = re.compile("[\u200b-\u200f\u2060\ufe00-\ufe0f\ufeff]")
STOP = set(
    "a an and are as at be by for from in into is it its of on or that the their "
    "them they this to was were which with whose who what than then there these "
    "those not no only one two all any each other such same very so".split()
)


def words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOP and len(w) > 2]


def stem(w: str) -> str:
    for suffix in ("ing", "ed", "es", "s"):
        if w.endswith(suffix) and len(w) - len(suffix) >= 4:
            return w[: -len(suffix)]
    return w


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a | b else 1.0


def random_k_jaccard(n: int, k: int) -> float:
    """Exact expected Jaccard between a random k-subset of n and a fixed gold k-subset."""
    total = 0.0
    count = 0
    for guess in combinations(range(n), k):
        total += jaccard(set(guess), set(range(k)))
        count += 1
    return total / count


def lexical_guess(items: list[dict], k: int) -> set[str]:
    docs = [Counter(stem(w) for w in words(f"{it['title']} {it['description']}")) for it in items]
    df = Counter(t for d in docs for t in d)
    n = len(docs)
    vecs = [{t: c * math.log((1 + n) / (1 + df[t])) for t, c in d.items()} for d in docs]

    def cos(a: dict, b: dict) -> float:
        num = sum(a[t] * b.get(t, 0.0) for t in a)
        den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
        return num / den if den else 0.0

    sims = [sum(cos(v, w) for j, w in enumerate(vecs) if j != i) for i, v in enumerate(vecs)]
    order = sorted(range(n), key=lambda i: sims[i])
    return {items[i]["id"] for i in order[:k]}


def length_guess(items: list[dict], k: int) -> set[str]:
    lens = [len(it["description"]) for it in items]
    med = statistics.median(lens)
    order = sorted(range(len(items)), key=lambda i: -abs(lens[i] - med))
    return {items[i]["id"] for i in order[:k]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    rows = [json.loads(line) for line in args.path.read_text().splitlines() if line.strip()]
    errors: list[str] = []
    leaks: list[str] = []
    scores: dict[str, list[float]] = {"random": [], "lexical": [], "length": []}
    by_tier: Counter = Counter()
    by_domain: Counter = Counter()
    title_use: Counter = Counter()
    thirds: Counter = Counter()

    for row in rows:
        info = row["info"]
        sid = info["spec_id"]
        items = info["items"]
        gold = set(row["answer"].split(","))
        by_tier[info["difficulty"]] += 1
        by_domain[info["domain"]] += 1
        if not 8 <= len(items) <= 12:
            errors.append(f"{sid}: {len(items)} items")
        if not 1 <= len(gold) <= 2:
            errors.append(f"{sid}: {len(gold)} intruders")
        if gold != {it["id"] for it in items if it["is_intruder"]}:
            errors.append(f"{sid}: answer does not match item flags")
        for it in items:
            if INVISIBLE.search(it["title"] + it["description"]):
                errors.append(f"{sid}/{it['id']}: invisible character in item text (a hidden cue)")
        titles = [it["title"].lower() for it in items]
        if len(set(titles)) != len(titles):
            errors.append(f"{sid}: duplicate titles within row")
        title_use.update(set(titles))
        for m in row["prompt"]:
            if m["role"] == "user" and info["theme"].lower() in m["content"].lower():
                errors.append(f"{sid}: theme text appears verbatim in prompt")

        # A theme word is only a leak if it separates members from intruders: shared
        # category words ("band", "tool") that intruders also carry give nothing away.
        theme_terms = {stem(w) for w in words(info["theme"])}
        bags = {it["id"]: {stem(w) for w in words(f"{it['title']} {it['description']}")} for it in items}
        in_intruders = set().union(*(bags[i] for i in gold))
        for it in items:
            hit = (theme_terms & bags[it["id"]]) - in_intruders
            if hit and not it["is_intruder"]:
                leaks.append(f"{sid}/{it['id']} {it['title']!r}: {sorted(hit)}")

        for pos, it in enumerate(items):
            if it["is_intruder"]:
                thirds[min(2, 3 * pos // len(items))] += 1

        k = len(gold)
        scores["random"].append(random_k_jaccard(len(items), k))
        scores["lexical"].append(jaccard(lexical_guess(items, k), gold))
        scores["length"].append(jaccard(length_guess(items, k), gold))

    themes = [(r["info"]["spec_id"], {stem(w) for w in words(r["info"]["theme"])}) for r in rows]
    for (a, ta), (b, tb) in combinations(themes, 2):
        if jaccard(ta, tb) >= 0.6:
            errors.append(f"near-duplicate themes: {a} ~ {b}")

    print(f"rows: {len(rows)}")
    print(f"tiers: {dict(by_tier)}")
    print(f"domains: {dict(by_domain)}")
    reused = {t: c for t, c in title_use.items() if c > 1}
    print(f"items reused across rows: {len(reused)}" + (f" {reused}" if args.verbose else ""))
    print("shortcut baselines (mean Jaccard, oracle k):")
    for name, vals in scores.items():
        print(f"  {name:8s} {statistics.mean(vals):.3f}")
    total = sum(thirds.values())
    shares = [thirds[i] / total for i in range(3)]
    print("intruder position (first/middle/last third): " + " / ".join(f"{x:.2f}" for x in shares))
    if len(rows) >= 50 and not all(0.2 <= x <= 0.47 for x in shares):
        errors.append(f"intruder positions are unbalanced: {shares}")
    print(f"theme-word leaks: {len(leaks)} item(s)")
    for leak in leaks if args.verbose else leaks[:10]:
        print(f"  {leak}")
    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
