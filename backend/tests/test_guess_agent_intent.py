import asyncio
import json
import sys
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.guess_agent import GuessAgent


def _build_agent() -> GuessAgent:
    settings = SimpleNamespace(
        agent_model_name="agent-model",
        agent_model_temperature=0,
        agent_model_api_key="test-key",
        agent_model_base_url="http://localhost",
        helper_model_name="helper-model",
        helper_model_temperature=0,
        helper_model_api_key="test-key",
        helper_model_base_url="http://localhost",
    )
    prompt_loader = MagicMock()
    prompt_loader.load_prompt.return_value = "turn_router prompt"
    memory_policy = MagicMock()
    memory_policy.build_recent_history.return_value = []
    memory_policy.build_summary.return_value = ""

    agent = GuessAgent(settings=settings, prompt_loader=prompt_loader, memory_policy=memory_policy)
    agent.agent_model = AsyncMock()
    return agent


def test_parse_user_intent_uses_structured_context_payload():
    async def run_test():
        agent = _build_agent()
        agent.agent_model.ainvoke.return_value = SimpleNamespace(
            content='{"intent":"question","normalized_text":"","guess_word":"","answer":"unknown","confidence":0.9,"reason":"ok"}'
        )

        history = [
            {
                "turn_type": "question",
                "input_text": "这个词是抽象的概念吗？",
                "answer_text": "pending",
            },
            {
                "turn_type": "answer",
                "input_text": "不是",
                "answer_text": "no",
            },
        ]

        result = await agent.parse_user_intent("它是文科相关的吗？", history)

        messages = agent.agent_model.ainvoke.call_args.args[0]
        assert len(messages) == 2

        payload = json.loads(messages[1]["content"])
        assert payload == {
            "context": {
                "last_turn": {
                    "type": "qa",
                    "question": "这个词是抽象的概念吗？",
                    "answer": "no",
                }
            },
            "current_input": "它是文科相关的吗？",
        }
        assert result["intent"] == "question"

    asyncio.run(run_test())


def test_parse_user_intent_prefers_pending_question_in_waiting_answer():
    async def run_test():
        agent = _build_agent()
        agent.agent_model.ainvoke.return_value = SimpleNamespace(
            content='{"intent":"answer","normalized_text":"yes","guess_word":"","answer":"yes","confidence":0.9,"reason":"ok"}'
        )

        history = [
            {
                "turn_type": "question",
                "input_text": "心理学相关概念吗？",
                "answer_text": "yes",
            },
            {
                "turn_type": "question",
                "input_text": "这个名字是中国人吗？",
                "answer_text": "pending",
            },
        ]

        await agent.parse_user_intent(
            "嗯",
            history,
            current_phase="waiting_answer",
            pending_question="这个名字是中国人吗？",
        )

        messages = agent.agent_model.ainvoke.call_args.args[0]
        payload = json.loads(messages[1]["content"])
        assert payload == {
            "context": {
                "last_turn": {
                    "type": "qa",
                    "question": "这个名字是中国人吗？",
                    "answer": "unknown",
                }
            },
            "current_input": "嗯",
        }

    asyncio.run(run_test())


def test_parse_user_intent_prefers_pending_guess_in_awaiting_judgement():
    async def run_test():
        agent = _build_agent()
        agent.agent_model.ainvoke.return_value = SimpleNamespace(
            content='{"intent":"judge","normalized_text":"yes","guess_word":"","answer":"yes","confidence":0.9,"reason":"ok"}'
        )

        history = [
            {
                "turn_type": "question",
                "input_text": "这个词是心理学相关概念吗？",
                "answer_text": "yes",
            },
            {
                "turn_type": "guess",
                "input_text": "认知失调",
                "answer_text": "pending",
            },
        ]

        await agent.parse_user_intent(
            "是",
            history,
            current_phase="awaiting_judgement",
            pending_guess="认知失调",
        )

        messages = agent.agent_model.ainvoke.call_args.args[0]
        payload = json.loads(messages[1]["content"])
        assert payload == {
            "context": {
                "last_turn": {
                    "type": "guess",
                    "guess_word": "认知失调",
                    "answer": "unknown",
                }
            },
            "current_input": "是",
        }

    asyncio.run(run_test())
