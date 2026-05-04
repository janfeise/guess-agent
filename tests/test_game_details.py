import os
import sys
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)
sys.path.insert(0, os.path.join(repo_root, "backend"))

from app.api.game_details import router as game_details_router
from app.api.user_games import router as user_games_router
from app.api.v1.games import get_game_service, router as games_router
from app.services.game_service import GameService


class FakeRepository:
    def __init__(self, game_doc):
        self.game_doc = game_doc

    async def get_game(self, game_id: str):
        if self.game_doc and self.game_doc.get("game_id") == game_id:
            return self.game_doc
        return None


class FakeService:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    async def get_game_details(self, game_id: str, user_id: str | None = None):
        self.calls.append((game_id, user_id))
        if self.error:
            raise self.error
        return self.response

    async def get_user_game_history(self, user_id: str):
        self.calls.append(("history", user_id))
        if self.error:
            raise self.error
        return self.response


def build_service(game_doc):
    repository = FakeRepository(game_doc)
    return GameService(settings=None, agent=None, repository=repository, memory_policy=None)


class FakeHistoryRepository:
    def __init__(self, game_docs):
        self.game_docs = game_docs

    async def list_games_by_owner(self, owner_id: str):
        return self.game_docs


def test_get_game_details_finished_returns_full_detail():
    service = build_service(
        {
            "game_id": "game-1",
            "status": "finished",
            "owner_id": "user-1",
            "difficulty": "hard",
            "user_word": "苹果",
            "round_count": 2,
            "summary": "Q:水果吗 A:是；Q:红色吗 A:否",
            "history": [
                {
                    "round_no": 1,
                    "actor": "user",
                    "turn_type": "question",
                    "input_text": "是水果吗",
                    "answer_text": "是",
                    "answer_label": "yes",
                    "hint": "",
                    "confidence": 0.9,
                    "result": "internal_reasoning_should_be_removed",
                    "visible_to_player": True,
                },
                {
                    "round_no": 2,
                    "actor": "system",
                    "turn_type": "guess",
                    "input_text": "苹果",
                    "answer_text": "pending",
                    "confidence": 0.6,
                    "result": "another_internal_reasoning",
                    "visible_to_player": False,
                },
            ],
            "metadata": {"phase": "finished", "next_actor": "user"},
            "created_at": datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 5, 4, 12, 30, tzinfo=timezone.utc),
            "finished_at": datetime(2026, 5, 4, 12, 31, tzinfo=timezone.utc),
            "finish_reason": "user_win",
            "system_word_encrypted": "encrypted-value",
            "target_word_source": "helper_llm",
        }
    )

    import asyncio

    payload = asyncio.run(service.get_game_details("game-1", user_id="user-1"))

    assert payload["status"] == "finished"
    assert payload["finish_reason"] == "user_win"
    assert payload["system_word_encrypted"] == "encrypted-value"
    assert payload["finished_at"] == datetime(2026, 5, 4, 12, 31, tzinfo=timezone.utc)
    assert len(payload["history"]) == 2
    assert "result" not in payload["history"][0]
    assert "result" not in payload["history"][1]
    assert "progress" not in payload


def test_get_game_details_in_progress_returns_progress_view():
    service = build_service(
        {
            "game_id": "game-2",
            "status": "active",
            "owner_id": "user-2",
            "difficulty": "medium",
            "user_word": "香蕉",
            "round_count": 3,
            "summary": "Q:水果吗 A:是",
            "history": [
                {
                    "round_no": 1,
                    "actor": "user",
                    "turn_type": "question",
                    "input_text": "它是水果吗",
                    "answer_text": "是",
                    "answer_label": "yes",
                    "hint": "",
                    "confidence": 0.8,
                    "result": "should_be_hidden",
                    "visible_to_player": True,
                },
                {
                    "round_no": 2,
                    "actor": "system",
                    "turn_type": "guess",
                    "input_text": "香蕉",
                    "answer_text": "pending",
                    "confidence": 0.7,
                    "result": "internal_only",
                    "visible_to_player": False,
                },
            ],
            "metadata": {
                "phase": "awaiting_judgement",
                "next_actor": "user",
                "expected_turn_type": "judge",
                "waiting_answer": False,
                "awaiting_judgement": True,
                "pending_question": "",
                "pending_guess": "香蕉",
                "agent_confidence": 0.7,
                "last_actor": "system",
                "last_intent": "guess",
            },
            "created_at": datetime(2026, 5, 4, 13, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 5, 4, 13, 15, tzinfo=timezone.utc),
        }
    )

    import asyncio

    payload = asyncio.run(service.get_game_details("game-2", user_id="user-2"))

    assert payload["status"] == "active"
    assert payload["progress"]["phase"] == "awaiting_judgement"
    assert payload["progress"]["pending_guess"] == "香蕉"
    assert len(payload["history"]) == 1
    assert payload["history"][0]["round_no"] == 1
    assert "result" not in payload["history"][0]
    assert payload.get("finished_at") is None


def test_get_game_details_forbidden_when_owner_mismatch():
    service = build_service(
        {
            "game_id": "game-3",
            "status": "active",
            "owner_id": "user-3",
            "history": [],
            "metadata": {},
            "created_at": datetime(2026, 5, 4, 14, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 5, 4, 14, 0, tzinfo=timezone.utc),
        }
    )

    import asyncio

    try:
        asyncio.run(service.get_game_details("game-3", user_id="other-user"))
    except PermissionError as exc:
        assert "not allowed" in str(exc)
    else:
        raise AssertionError("PermissionError was not raised")


def test_get_user_game_history_calls_detail_service_for_each_game():
    repository = FakeHistoryRepository([
        {"game_id": "game-6"},
        {"game_id": "game-7"},
    ])
    service = GameService(settings=None, agent=None, repository=repository, memory_policy=None)

    async def fake_get_game_details(game_id: str, user_id: str | None = None):
        return {
            "game_id": game_id,
            "status": "finished" if game_id == "game-6" else "active",
            "owner_id": user_id,
            "difficulty": "medium",
            "user_word": "测试",
            "round_count": 1,
            "summary": "",
            "history": [],
            "metadata": {},
            "created_at": datetime(2026, 5, 4, 17, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 5, 4, 17, 1, tzinfo=timezone.utc),
        }

    service.get_game_details = fake_get_game_details  # type: ignore[assignment]

    import asyncio

    payload = asyncio.run(service.get_user_game_history("user-6"))

    assert payload["user_id"] == "user-6"
    assert payload["total"] == 2
    assert [item["game_id"] for item in payload["games"]] == ["game-6", "game-7"]


def build_test_app(fake_service):
    app = FastAPI()
    app.include_router(game_details_router, prefix="/api")
    app.include_router(user_games_router, prefix="/api")
    app.include_router(games_router, prefix="/api/v1")
    app.dependency_overrides[get_game_service] = lambda: fake_service
    return app


def test_new_details_route_works():
    fake_service = FakeService(
        {
            "game_id": "game-4",
            "status": "active",
            "owner_id": "user-4",
            "difficulty": "easy",
            "user_word": "梨",
            "round_count": 1,
            "summary": "",
            "history": [],
            "metadata": {"phase": "user_turn"},
            "created_at": datetime(2026, 5, 4, 15, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 5, 4, 15, 1, tzinfo=timezone.utc),
            "progress": {"phase": "user_turn"},
        }
    )
    client = TestClient(build_test_app(fake_service))

    response = client.get("/api/game/game-4/details", params={"userId": "user-4"})

    assert response.status_code == 200
    assert response.json()["game_id"] == "game-4"
    assert fake_service.calls == [("game-4", "user-4")]


def test_compat_details_route_works():
    fake_service = FakeService(
        {
            "game_id": "game-5",
            "status": "finished",
            "owner_id": "user-5",
            "difficulty": "hard",
            "user_word": "橙子",
            "round_count": 2,
            "summary": "",
            "history": [],
            "metadata": {},
            "created_at": datetime(2026, 5, 4, 16, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 5, 4, 16, 1, tzinfo=timezone.utc),
            "finished_at": datetime(2026, 5, 4, 16, 2, tzinfo=timezone.utc),
            "finish_reason": "user_win",
            "system_word_encrypted": "encrypted-value",
            "target_word_source": "helper_llm",
        }
    )
    client = TestClient(build_test_app(fake_service))

    response = client.get("/api/v1/games/game-5", params={"userId": "user-5"})

    assert response.status_code == 200
    assert response.json()["finish_reason"] == "user_win"
    assert fake_service.calls == [("game-5", "user-5")]


def test_user_game_history_route_works():
    fake_service = FakeService(
        {
            "user_id": "user-7",
            "total": 1,
            "games": [
                {
                    "game_id": "game-8",
                    "status": "finished",
                    "owner_id": "user-7",
                    "difficulty": "easy",
                    "user_word": "柚子",
                    "round_count": 2,
                    "summary": "",
                    "history": [],
                    "metadata": {},
                    "created_at": datetime(2026, 5, 4, 18, 0, tzinfo=timezone.utc),
                    "updated_at": datetime(2026, 5, 4, 18, 1, tzinfo=timezone.utc),
                    "finished_at": datetime(2026, 5, 4, 18, 2, tzinfo=timezone.utc),
                    "finish_reason": "user_win",
                    "system_word_encrypted": "encrypted-value",
                    "target_word_source": "helper_llm",
                }
            ],
        }
    )
    client = TestClient(build_test_app(fake_service))

    response = client.get("/api/user/games/history", params={"userId": "user-7"})

    assert response.status_code == 200
    assert response.json()["user_id"] == "user-7"
    assert response.json()["total"] == 1
    assert response.json()["games"][0]["game_id"] == "game-8"
    assert fake_service.calls == [("history", "user-7")]
