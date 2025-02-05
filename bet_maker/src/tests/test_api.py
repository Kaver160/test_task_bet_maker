import pytest
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport
from fastapi import status
from aioresponses import aioresponses

from src.config import settings

load_dotenv()
from src.main import app

data_events = {'1': {
    "id": "1",
    "coefficient": "1.2",
    "deadline": "2025-01-31T11:55:18.952060",
    "status": "unfinished"
},
    '2':
        {
            "id": "2",
            "coefficient": "1.15",
            "deadline": "2025-02-03T11:55:18.952111",
            "status": "unfinished"
        },
    '3':
        {
            "id": "3",
            "coefficient": "1.67",
            "deadline": "2025-02-05T11:55:18.952125",
            "status": "unfinished"
        }
}


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_events(async_client):
    external_api_url = f'{settings.line_provider_url}/events'
    with aioresponses() as m:
        m.get(external_api_url, payload=data_events, status=200)
        response = await async_client.get("/events")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_bet(async_client):
    bet_data = {
        "event_id": "1",
        "amount": 100.0
    }
    response = await async_client.post("/beta", json=bet_data)
    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response["event_id"] == bet_data["event_id"]
    assert json_response["amount"] == bet_data["amount"]


@pytest.mark.asyncio
async def test_read_bets(async_client):
    bet_data = {
        "event_id": "34",
        "amount": 232.0,
        "status": "pending"
    }
    # Предварительное создание ставки
    await async_client.post("/beta", json=bet_data)
    response = await async_client.get("/bets")
    assert response.status_code == 200
    json_response = response.json()
    assert isinstance(json_response, list)
    assert json_response[0]["event_id"] == bet_data["event_id"]
    assert json_response[0]["amount"] == bet_data["amount"]


@pytest.mark.asyncio
async def test_update_bet_status(async_client):
    status_data = {"status": "team1_won"}
    response = await async_client.put("/bets/1", json=status_data)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["status"]
