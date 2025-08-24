import pytest

BASE = "/api/v1/user/"


@pytest.mark.django_db
def test_user_registration(api_client):
    payload = {"username": "testuser", "password": "testpass123"}
    resp = api_client.post(BASE + "register/", payload, format="json")

    assert resp.status_code == 201
    assert "id" in resp.data


@pytest.mark.django_db
def test_user_login(api_client, user):
    payload = {"username": user.username, "password": "testpass123"}
    resp = api_client.post(BASE + "token/", payload, format="json")

    assert resp.status_code == 200
    assert "access" in resp.data


@pytest.mark.django_db
def test_get_me_requires_auth(api_client):
    resp = api_client.get(BASE + "me/")

    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_get_me_authenticated(auth_client, user):
    resp = auth_client.get(BASE + "me/")

    assert resp.status_code == 200
    assert resp.data["email"] == user.email
