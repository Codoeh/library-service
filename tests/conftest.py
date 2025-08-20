from datetime import timezone, date, timedelta

import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory, AdminFactory, BookFactory
from unittest.mock import patch


@pytest.fixture
def api_client():
    """DRF client without authentication."""
    return APIClient()

@pytest.fixture
def user(db):
    """Normal user in DB."""
    return UserFactory()

@pytest.fixture
def admin_user(db):
    """Admin user in DB."""
    return AdminFactory()

@pytest.fixture
def auth_client(api_client, user):
    """Client authenticated as normal user."""
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    """Client authenticated as admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.fixture
def mock_send():
    with patch("utils.telegram_helper.send_telegram_message") as mock:
        yield mock

@pytest.fixture
def mock_stripe_create():
    with patch("utils.stripe_helper.stripe.checkout.Session.create") as mock:
        mock.return_value = type("S", (), {
            "id": "sess_123",
            "url": "http://fake/checkout",
        })()
        yield mock

@pytest.fixture
def mock_stripe_retrieve():
    with patch("payments.views.stripe.checkout.Session.retrieve") as mock:
        mock.return_value = type("S", (), {"payment_status": "paid"})()
        yield mock