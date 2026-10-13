"""API behavior and authorization tests."""

from fastapi.testclient import TestClient

AUTH = {"Authorization": "Bearer unit-test-token"}


def create(client: TestClient, **overrides: object):
    payload = {"title": "Email delivery failed", "priority": "high", **overrides}
    return client.post("/tickets", json=payload, headers=AUTH)


def test_health_is_public(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tickets_require_authentication(client: TestClient):
    assert client.get("/tickets").status_code == 401
    assert client.get("/tickets", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert client.get("/tickets", headers=AUTH).status_code == 200


def test_create_read_update_delete_ticket(client: TestClient):
    created = create(client)
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "open"
    assert body["priority"] == "high"
    assert body["id"] > 0
    assert body["created_at"]

    ticket_id = body["id"]
    fetched = client.get(f"/tickets/{ticket_id}", headers=AUTH)
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Email delivery failed"

    edited = client.patch(
        f"/tickets/{ticket_id}",
        json={"status": "in_progress", "assigned_to": "alex"},
        headers=AUTH,
    )
    assert edited.status_code == 200
    assert edited.json()["assigned_to"] == "alex"

    deleted = client.delete(f"/tickets/{ticket_id}", headers=AUTH)
    assert deleted.status_code == 204
    assert client.get(f"/tickets/{ticket_id}", headers=AUTH).status_code == 404


def test_filter_sort_paginate(client: TestClient):
    assert create(client, title="First", priority="low").status_code == 201
    assert create(client, title="Second", priority="high", assigned_to="sam").status_code == 201
    assert create(client, title="Third", priority="high", assigned_to="sam").status_code == 201

    result = client.get(
        "/tickets",
        params={"priority": "high", "assigned_to": "sam", "sort": "oldest", "limit": 1},
        headers=AUTH,
    )
    assert result.status_code == 200
    data = result.json()
    assert data["total"] == 2
    assert data["limit"] == 1
    assert data["items"][0]["title"] == "Second"

    second_page = client.get(
        "/tickets", params={"priority": "high", "offset": 1, "limit": 1}, headers=AUTH
    )
    assert second_page.json()["total"] == 2
    assert second_page.json()["items"][0]["title"] == "Second"


def test_validation_and_missing_ticket(client: TestClient):
    assert create(client, title="").status_code == 422
    assert create(client, priority="urgent").status_code == 422
    assert client.get("/tickets/999", headers=AUTH).status_code == 404
    created = create(client)
    ticket_id = created.json()["id"]
    assert client.patch(
        f"/tickets/{ticket_id}", json={"title": None}, headers=AUTH
    ).status_code == 422
    assert client.get("/tickets", params={"limit": 101}, headers=AUTH).status_code == 422
