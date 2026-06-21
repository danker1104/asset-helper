from datetime import datetime, timezone

import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_learning_card_completion_increments_growth() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        signup = await client.post(
            "/auth/signup",
            json={"user_id": "demo", "email": "demo@example.com", "baseline_amount": 30000},
        )
        assert signup.status_code == 200

        cards_response = await client.get("/learning/cards")
        assert cards_response.status_code == 200
        cards = cards_response.json()["items"]
        assert any(card["id"] == "budget-basics" for card in cards)

        complete_response = await client.post(
            "/learning/cards/budget-basics/complete",
            json={"user_id": "demo", "completed_at": datetime.now(timezone.utc).isoformat()},
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["growth"] == 1

        avatar_response = await client.get("/avatar", params={"user_id": "demo"})
        assert avatar_response.status_code == 200
        assert avatar_response.json()["growth"] == 1


@pytest.mark.asyncio
async def test_learning_card_duplicate_completion_does_not_add_growth() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/auth/signup",
            json={"user_id": "demo", "email": "demo@example.com", "baseline_amount": 30000},
        )

        first = await client.post(
            "/learning/cards/budget-basics/complete",
            json={"user_id": "demo", "completed_at": datetime.now(timezone.utc).isoformat()},
        )
        second = await client.post(
            "/learning/cards/budget-basics/complete",
            json={"user_id": "demo", "completed_at": datetime.now(timezone.utc).isoformat()},
        )

        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json()["growth"] == 1
        assert second.json()["growth"] == 1
