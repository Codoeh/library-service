import pytest
from tests.factories import BookFactory

BASE = "/api/v1/books/"


new_book_payload = {
        "title": "New",
        "author": "A",
        "cover": "SOFT",
        "inventory": 2,
        "daily_fee": "1.20",
    }

@pytest.mark.django_db
def test_list_books_without_auth(api_client):
    """Every user (even not authenticated) should be able to get list view."""
    BookFactory.create_batch(3)
    resp = api_client.get(BASE)

    assert resp.status_code == 200
    assert len(resp.data) >= 3

@pytest.mark.django_db
def test_create_book_requires_admin(auth_client):
    """Normal user shouldn't be able to create a new book."""
    payload = new_book_payload
    resp = auth_client.post(BASE, payload, format="json")

    assert resp.status_code in (403, 401)

@pytest.mark.django_db
def test_admin_create_book(admin_client):
    """Admin user should be able to create a new book."""
    payload = new_book_payload
    resp = admin_client.post(BASE, payload, format="json")

    assert resp.status_code == 201
    assert resp.data["title"] == "New"

@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload,expected_error",
    [
        pytest.param({
            "author": "A",
            "cover": "SOFT",
            "inventory": 2,
            "daily_fee": "1.20"
        },
        "title",
        id="no title",
        ),
        pytest.param({
            "title": "New",
            "cover": "SOFT",
            "inventory": 2,
            "daily_fee": "1.20",
        },
        "author",
        id="no author",
        ),
        pytest.param({
            "title": "New",
            "author": "A",
            "inventory": 2,
            "daily_fee": "1.20",
        },
        "cover",
        id="no cover",
        ),
        pytest.param({
            "title": "New",
            "author": "A",
            "cover": "SOFT",
            "inventory": -2,
            "daily_fee": "1.20",
        },
        "inventory",
        id="negative inventory",
        ),
        pytest.param({
            "title": "New",
            "author": "A",
            "cover": "SOFT",
            "inventory": 2,
        },
        "daily_fee",
        id="no daily_fee",
        ),
    ]
)
def test_create_book_with_not_valid_data(admin_client, payload, expected_error):
    """Try to create book with different not valid datas."""
    resp = admin_client.post(BASE, payload, format="json")
    assert resp.status_code == 400
    assert expected_error in resp.data

@pytest.mark.django_db
def test_delete_book(admin_client):
    """Admin user should be able to delete book."""
    book = BookFactory()
    resp = admin_client.delete(f"{BASE}{book.id}/")
    assert resp.status_code == 204