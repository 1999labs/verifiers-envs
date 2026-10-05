import subprocess
import sys
from pathlib import Path

import pytest

import verifiers.v1 as vf
from curators_eye.taskset import (
    CuratorsEyeConfig,
    CuratorsEyeTaskset,
    ThemeJudge,
    parse_intruders,
    parse_theme,
)
from verifiers.v1.graph import MessageNode
from verifiers.v1.types import AssistantMessage, UserMessage

ROOT = Path(__file__).resolve().parents[1]
NO_KEY = "CURATORS_EYE_TEST_UNSET_KEY"


def load(**config) -> list:
    return CuratorsEyeTaskset(CuratorsEyeConfig(**config)).load()


def with_key_var(task, var: str):
    """A copy of `task` whose judge reads its key from `var`."""
    config = task.config.model_copy(
        update={"judge": task.config.judge.model_copy(update={"api_key_var": var})}
    )
    return type(task)(task.data, config)


def trace_for(task, reply: str) -> vf.Trace:
    return vf.Trace(
        agent=vf.AgentInfo(config=vf.AgentConfig()),
        task=vf.TraceTask(type=type(task).__name__, data=task.data),
        nodes=[
            MessageNode(parent=None, message=UserMessage(content=task.data.prompt), sampled=False),
            MessageNode(parent=0, message=AssistantMessage(content=reply), sampled=True),
        ],
    )


async def score(task, reply: str) -> vf.Trace:
    trace = trace_for(task, reply)
    await task.score(trace)
    return trace


def test_dataset_loads_and_is_consistent() -> None:
    tasks = load()
    assert len(tasks) >= 10
    assert len({t.key for t in tasks}) == len(tasks)
    for t in tasks:
        items = t.data.info["items"]
        assert 8 <= len(items) <= 12
        assert t.data.answer.split(",") == sorted(i["id"] for i in items if i["is_intruder"])
        assert t.data.info["theme"] not in t.data.prompt
        for item in items:
            assert f"{item['id']}. {item['title']}: " in t.data.prompt


def test_filters_and_splits_partition_the_data() -> None:
    all_keys = {t.key for t in load()}
    train = {t.key for t in load(split="train")}
    held = {t.key for t in load(split="eval")}
    assert train and held and not train & held and train | held == all_keys
    subtle = load(difficulty=["subtle"])
    assert subtle and all(t.data.info["difficulty"] == "subtle" for t in subtle)


def test_dataset_passes_validator() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "data_gen/validate_dataset.py"), str(ROOT / "curators_eye/data/curators_eye.jsonl")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("reply", "expected"),
    [
        ("<intruders>C, K</intruders>", {"C", "K"}),
        ("<intruders>c;k</intruders>", {"C", "K"}),
        ("<intruders>B</intruders> then <intruders>D and E</intruders>", {"D", "E"}),
        ("<intruders></intruders>", set()),
        ("The intruders are C and K.", None),
    ],
)
def test_parse_intruders(reply: str, expected) -> None:
    assert parse_intruders(reply) == expected


def test_parse_theme() -> None:
    assert parse_theme("<intruders>A</intruders>\n<theme> Things named for people. </theme>") == (
        "Things named for people."
    )
    assert parse_theme("no tags") == ""


async def test_reward_without_judge_is_intruder_score() -> None:
    task = with_key_var(load()[0], NO_KEY)
    gold = task.data.answer.split(",")
    wrong = next(i["id"] for i in task.data.info["items"] if not i["is_intruder"])

    exact = await score(task, f"<intruders>{','.join(gold)}</intruders><theme>x</theme>")
    assert exact.rewards["intruders"].score == 1.0
    assert exact.reward == pytest.approx(1.0)
    assert exact.metrics["exact_match"] == 1.0 and exact.metrics["judged"] == 0.0

    miss = await score(task, f"<intruders>{wrong}</intruders><theme>x</theme>")
    assert miss.reward == 0.0 and miss.metrics["exact_match"] == 0.0

    partial = await score(task, f"<intruders>{gold[0]},{wrong}</intruders><theme>x</theme>")
    expected = 1 / (len(gold) + 1)  # Jaccard: one hit, the union adds the wrong guess
    assert partial.reward == pytest.approx(expected)

    unformatted = await score(task, f"I think it's {','.join(gold)}.")
    assert unformatted.reward == 0.0 and unformatted.metrics["format_ok"] == 0.0


async def test_flagging_everything_scores_low() -> None:
    task = with_key_var(load()[0], NO_KEY)
    everything = ",".join(i["id"] for i in task.data.info["items"])
    trace = await score(task, f"<intruders>{everything}</intruders><theme>x</theme>")
    assert trace.reward <= 2 / 8


async def test_judge_grades_theme(monkeypatch) -> None:
    monkeypatch.setenv("CURATORS_EYE_TEST_KEY", "sk-test")
    task = with_key_var(load()[0], "CURATORS_EYE_TEST_KEY")
    seen = {}

    async def fake_complete(self, messages, *, trace=None, schema=None, parse=None, **_):
        seen["prompt"] = messages
        response = vf.JudgeResponse(text="Too broad.\nFINAL VERDICT: B")
        response.parsed = parse(response)
        return response

    monkeypatch.setattr(ThemeJudge, "complete", fake_complete)
    gold = task.data.answer
    trace = await score(task, f"<intruders>{gold}</intruders><theme>Board games.</theme>")
    assert trace.rewards["theme"].score == 0.5
    assert trace.reward == pytest.approx(0.7 * 1.0 + 0.3 * 0.5)
    assert trace.metrics["judged"] == 1.0
    assert task.data.info["theme"] in seen["prompt"] and "Board games." in seen["prompt"]

    empty = await score(task, f"<intruders>{gold}</intruders>")
    assert empty.rewards["theme"].score == 0.0
