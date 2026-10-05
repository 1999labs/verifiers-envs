# Authoring curators-eye theme specs

Each spec is one hidden organizing principle. `build_dataset.py` turns every spec
into one dataset row, and `validate_dataset.py` gates the result.
`specs/samples.json` is the reference for tone and quality.

## Schema

```json
{
  "id": "domain-short-slug",
  "domain": "design objects | music | food | architecture | internet culture | tools | games",
  "tier": "obvious | moderate | subtle",
  "theme": "One sentence stating the principle precisely enough to judge edge cases.",
  "decoy": "The looser surface theme that the members AND the intruders all satisfy.",
  "members": [{"title": "...", "description": "..."}],
  "intruders": [{"title": "...", "description": "...", "why": "..."}]
}
```

- 8 to 10 members, all satisfying the theme.
- 1 to 3 intruders. The builder samples one or two of them per row.
- `why` names the fact that violates the theme, and says what makes the intruder
  look like it belongs.

## What makes a good spec

1. **Genuine near-misses.** Every intruder must satisfy the decoy and look like it
   belongs on first read: same domain, era, register, and fame level as the
   members. Pick the item people commonly *misremember* as fitting. Good examples
   are Chicken Marengo among dishes named for people (it's a battle) and French
   horn among woodwinds (the English horn is a woodwind). Never add a random
   item or an obvious category mismatch.
2. **No keyword solving.** No word or phrase from the theme may appear in member
   text unless it appears in intruder text too. No title pattern (shared suffix,
   shared word, capitalization) may separate members from intruders.
   Descriptions describe the item and never mention the property the theme is
   about. For example, don't write "named after..." or "invented by accident".
3. **Uniform descriptions.** One line, roughly 6 to 16 words. Intruder
   descriptions match member descriptions in length, style, and specificity. The
   validator runs a length and word-overlap odd-one-out solver, and those
   solvers must not beat random.
4. **Factual certainty.** Use only facts you are highly confident are true and
   well documented. Skip contested origin legends, anything that can change over
   time ("still operating", "current record holder", "best-selling"), and
   borderline members. If you are unsure whether an item qualifies, leave it out.
5. **Tiers.**
   - `obvious`: the principle is a well-known category or property. The
     intruder violates it in a way most educated people would see once they
     think about it.
   - `moderate`: the principle needs a specific fact about each item (origin,
     maker, date, mechanism, material). Intruders share the domain and the
     salient surface feature.
   - `subtle`: the principle is second-order, structural, or abstract. Examples
     are properties of the name, counterfactual history, how the thing is made
     or used, or a relation to something else. The decoy is a strong alternative
     theme that explains every item, so the solver must find the tighter rule.
6. **Variety.** Don't reuse a principle family that is already taken. Keep
   themes distinct from each other and from the samples, and don't reuse items
   that appear in other specs.
7. **Tone.** No slurs, sexual content, graphic violence, real living private
   individuals, or politically charged topics.
