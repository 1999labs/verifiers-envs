"""curators-eye: spot the near-miss intruders in a curated collection (single-turn).

The model sees 8-12 items (title + one-line description) chosen by an unstated
organizing principle. One or two are near-miss intruders that share a looser
surface theme but break the principle. The model answers with
`<intruders>IDs</intruders><theme>...</theme>`.

Rewards (weighted sum, max 1.0):
  intruders (0.7)  Jaccard overlap of predicted vs. gold intruder IDs; exact set = 1.0.
  theme     (0.3)  LLM judge grades the stated theme against the hidden one. With no
                   judge API key the judge is skipped and this slot mirrors the
                   intruder score, so the reward still spans 0-1 on intruders alone.
"""

import json
import re
from pathlib import Path
from typing import Literal

import verifiers.v1 as vf
from verifiers.v1.configs.client import resolve_api_key
from verifiers.v1.judge import judge_verdict

DATA_PATH = Path(__file__).parent / "data" / "curators_eye.jsonl"
_INTRUDERS = re.compile(r"<intruders>(.*?)</intruders>", re.DOTALL | re.IGNORECASE)
_THEME = re.compile(r"<theme>(.*?)</theme>", re.DOTALL | re.IGNORECASE)

Difficulty = Literal["obvious", "moderate", "subtle"]


def parse_intruders(reply: str) -> set[str] | None:
    """Item IDs inside the last <intruders> tag, or None if the tag is missing."""
    matches = _INTRUDERS.findall(reply or "")
    if not matches:
        return None
    return {tok.upper() for tok in re.findall(r"\b[A-Za-z]\b", matches[-1])}


def parse_theme(reply: str) -> str:
    matches = _THEME.findall(reply or "")
    return matches[-1].strip() if matches else ""


def jaccard(pred: set[str], gold: set[str]) -> float:
    return len(pred & gold) / len(pred | gold) if pred | gold else 0.0


class ThemeJudge(vf.Judge[float]):
    prompt = """\
You are grading whether a solver identified the hidden organizing principle of a curated collection.

Hidden principle (ground truth): {theme}
Surface decoy (a looser theme that also fits the intruders; naming it is NOT enough): {decoy}

Solver's stated principle: {response}

Grade:
A - Same principle as the ground truth (paraphrase is fine; it would sort items the same way).
B - Partially right: on the right track but too broad, too narrow, or missing the key constraint.
C - Wrong, empty, or only restates the surface decoy.

Reply with a one-sentence justification, then "FINAL VERDICT: A", "FINAL VERDICT: B", or "FINAL VERDICT: C"."""

    def parse(self, response: vf.JudgeResponse[float]) -> float:
        verdict = judge_verdict(response.text, ("A", "B", "C"))
        return {"A": 1.0, "B": 0.5, "C": 0.0}[verdict]


class CuratorsEyeData(vf.TaskData):
    answer: str
    """Comma-joined gold intruder IDs, e.g. "C,K"."""
    info: dict
    """Hidden theme, decoy, difficulty, domain, split, and every item with its truth flag."""


class CuratorsEyeTaskConfig(vf.TaskConfig):
    judge: vf.JudgeConfig = vf.JudgeConfig()
    """Theme judge endpoint; skipped (graceful fallback) when its API key is unset."""


class CuratorsEyeTask(vf.Task[CuratorsEyeData, vf.State, CuratorsEyeTaskConfig]):
    @property
    def key(self) -> str:
        return self.data.info["spec_id"]

    @property
    def gold(self) -> set[str]:
        return set(self.data.answer.split(","))

    def judge_available(self) -> bool:
        return resolve_api_key(self.config.judge) != "EMPTY"

    @vf.stop
    async def single_turn(self, trace: vf.Trace) -> bool:
        return trace.num_turns >= 1

    @vf.reward(weight=0.7)
    async def intruders(self, trace: vf.Trace) -> float:
        return jaccard(parse_intruders(trace.last_reply) or set(), self.gold)

    @vf.reward(weight=0.3)
    async def theme(self, trace: vf.Trace) -> float:
        if not self.judge_available():
            return await self.intruders(trace)
        stated = parse_theme(trace.last_reply)
        if not stated:
            return 0.0
        result = await ThemeJudge(self.config.judge).evaluate(
            trace=trace,
            theme=self.data.info["theme"],
            decoy=self.data.info["decoy"],
            response=stated,
        )
        return float(result.parsed)

    @vf.metric
    async def exact_match(self, trace: vf.Trace) -> float:
        return float(parse_intruders(trace.last_reply) == self.gold)

    @vf.metric
    async def format_ok(self, trace: vf.Trace) -> float:
        reply = trace.last_reply
        return float(parse_intruders(reply) is not None and bool(parse_theme(reply)))

    @vf.metric
    async def judged(self, trace: vf.Trace) -> float:
        return float(self.judge_available())


class CuratorsEyeConfig(vf.TasksetConfig):
    split: Literal["train", "eval", "all"] = "all"
    """Theme-disjoint split; `all` uses every row."""
    difficulty: list[Difficulty] = ["obvious", "moderate", "subtle"]
    """Keep only rows of these tiers."""
    dataset: str = ""
    """Optional HF Hub dataset id with the same columns; empty uses the bundled JSONL."""
    task: CuratorsEyeTaskConfig = CuratorsEyeTaskConfig()


class CuratorsEyeTaskset(vf.Taskset[CuratorsEyeTask, CuratorsEyeConfig]):
    def load(self) -> list[CuratorsEyeTask]:
        if self.config.dataset:
            from datasets import load_dataset

            rows = list(load_dataset(self.config.dataset, split="train"))
        else:
            rows = [json.loads(line) for line in DATA_PATH.read_text().splitlines() if line]
        rows = [
            r
            for r in rows
            if r["info"]["difficulty"] in self.config.difficulty
            and self.config.split in ("all", r["info"]["split"])
        ]
        tasks = []
        for i, row in enumerate(rows):
            system, user = row["prompt"]
            tasks.append(
                CuratorsEyeTask(
                    CuratorsEyeData(
                        idx=i,
                        name=row["info"]["spec_id"],
                        system_prompt=system["content"],
                        prompt=user["content"],
                        answer=row["answer"],
                        info=row["info"],
                    ),
                    self.config.task,
                )
            )
        return tasks
