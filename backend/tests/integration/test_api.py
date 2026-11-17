import pytest

RATES_URL = "/api/v1/rates"
HISTORY_URL = "/api/v1/history"


def test_health_is_public(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_rates_requires_api_key(client):
    response = client.get(RATES_URL, params={"base": "USD", "target": "ARS"})

    assert response.status_code == 401


def test_rates_rejects_wrong_api_key(client):
    response = client.get(
        RATES_URL,
        params={"base": "USD", "target": "ARS"},
        headers={"X-API-Key": "wrong"},
    )

    assert response.status_code == 401


def test_rates_returns_the_rate(client, auth_headers):
    response = client.get(
        RATES_URL, params={"base": "USD", "target": "ARS"}, headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json() == {"base": "USD", "target": "ARS", "rate": 1000.0}


def test_rates_accepts_lowercase_codes(client, auth_headers):
    response = client.get(
        RATES_URL, params={"base": "usd", "target": "ars"}, headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["base"] == "USD"


def test_rates_unsupported_currency_returns_422(client, auth_headers):
    response = client.get(
        RATES_URL, params={"base": "USD", "target": "XYZ"}, headers=auth_headers
    )

    assert response.status_code == 422


def test_rates_validates_code_length(client, auth_headers):
    response = client.get(
        RATES_URL, params={"base": "US", "target": "ARS"}, headers=auth_headers
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "params",
    [
        {"target": "ARS"},
        {"base": "USD"},
        {"base": "USDD", "target": "ARS"},
        {"base": "USD", "target": "ARSS"},
    ],
)
def test_rates_rejects_missing_or_overlong_codes(client, auth_headers, params):
    response = client.get(RATES_URL, params=params, headers=auth_headers)

    assert response.status_code == 422


def test_history_requires_api_key(client):
    assert client.get(HISTORY_URL).status_code == 401


def test_history_is_empty_at_the_beginning(client, auth_headers):
    response = client.get(HISTORY_URL, headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_history_lists_queries_newest_first(client, auth_headers):
    client.get(RATES_URL, params={"base": "USD", "target": "ARS"}, headers=auth_headers)
    client.get(RATES_URL, params={"base": "EUR", "target": "USD"}, headers=auth_headers)

    response = client.get(HISTORY_URL, headers=auth_headers)

    assert [item["base"] for item in response.json()] == ["EUR", "USD"]


def test_rates_and_history_use_sqlalchemy_repository(sqlalchemy_client, auth_headers):
    first = sqlalchemy_client.get(
        RATES_URL, params={"base": "USD", "target": "ARS"}, headers=auth_headers
    )
    second = sqlalchemy_client.get(
        RATES_URL, params={"base": "EUR", "target": "USD"}, headers=auth_headers
    )

    assert first.status_code == 200
    assert second.status_code == 200

    history = sqlalchemy_client.get(HISTORY_URL, headers=auth_headers)

    assert history.status_code == 200
    assert [item["base"] for item in history.json()] == ["EUR", "USD"]
