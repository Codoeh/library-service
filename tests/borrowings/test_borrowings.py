from datetime import timezone, timedelta, date
from decimal import Decimal

import pytest

from borrowings.models import Borrowing
from tests.conftest import auth_client, admin_client, admin_user
from tests.factories import BorrowingFactory, BookFactory, UserFactory, AdminFactory

BASE = "/api/v1/borrowings/"


@pytest.mark.django_db
def test_create_borrowing_decrements_inventory(admin_client, mock_stripe_create):
    """Inventory should decrease by 1 on every borrowing create."""
    book = BookFactory(inventory=5)
    user = UserFactory()

    payload = {
        "book": book.id,
        "user": user.id,
        "expected_return_date": (date.today() + timedelta(days=5)).isoformat(),
    }

    resp = admin_client.post(BASE, payload, format="json")

    assert resp.status_code == 201
    book.refresh_from_db()
    assert book.inventory == 4


@pytest.mark.django_db
def test_normal_user_sees_only_own_borrowings(auth_client):
    """Normal user should see only his own borrowings."""
    user1 = UserFactory()
    user2 = UserFactory()

    BorrowingFactory.create_batch(3, user=user1)
    BorrowingFactory.create_batch(2, user=user2)

    auth_client.force_authenticate(user=user1)
    resp = auth_client.get(BASE, user=user1)

    assert resp.status_code == 200
    assert len(resp.data) == 3


@pytest.mark.django_db
def test_admin_can_filter_by_user(admin_client):
    """Admin user should be able to filter borrowings by user id."""
    user1 = UserFactory()
    user2 = UserFactory()
    admin = AdminFactory()

    BorrowingFactory.create_batch(3, user=user1)
    BorrowingFactory.create_batch(2, user=user2)
    BorrowingFactory.create_batch(1, user=admin)

    resp = admin_client.get(BASE, {"user_id": user1.id})

    assert resp.status_code == 200
    assert len(resp.data) == 3

@pytest.mark.django_db
def test_return_borrowing_creates_fine_if_overdue(auth_client, mock_stripe_create):
    """Borrowing status should be fine if return is overdue."""
    user = UserFactory()
    book = BookFactory()

    payload = {
        "book": book.id,
        "user": user.id,
        "borrow_date": (date.today() - timedelta(days=6)).isoformat(),
        "expected_return_date": (date.today() - timedelta(days=5)).isoformat()
    }
    auth_client.force_authenticate(user=user)
    resp = auth_client.post(BASE, payload, format="json")
    assert resp.status_code == 201
    borrowing_id = resp.data["id"]

    resp = auth_client.post(BASE + f"{borrowing_id}/return_book/")
    print(resp.data)
    assert resp.status_code == 200
    borrowing = Borrowing.objects.get(id=borrowing_id)
    borrowing.refresh_from_db()
    payment = borrowing.payments.first()
    payment.refresh_from_db()
    assert payment.type == "FINE"


@pytest.mark.django_db
def test_create_borrowing_book_out_of_stock(admin_client, mock_stripe_create):
    """Borrowing shouldn't be created if book's inventory is equal to 0."""
    book = BookFactory(inventory=0)
    user = UserFactory()

    payload = {
        "book": book.id,
        "user": user.id,
        "expected_return_date": (date.today() + timedelta(days=5)).isoformat(),
    }

    resp = admin_client.post(BASE, payload, format="json")

    assert resp.status_code == 400
    book.refresh_from_db()
    assert book.inventory == 0


@pytest.mark.django_db
def test_actual_return_date_cleared_when_created(admin_client):
    """Actual_return_date field should be automatically cleared after borrowing creation."""
    book = BookFactory()
    admin = AdminFactory()

    payload = {
        "book": book.id,
        "user": admin.id,
        "expected_return_date": (date.today() + timedelta(days=5)).isoformat(),
        "actual_return_date": (date.today()).isoformat()
    }

    resp = admin_client.post(BASE, payload, format="json")

    assert resp.status_code == 201
    assert resp.data["actual_return_date"] is None

@pytest.mark.django_db
def test_create_borrowing_creates_payment_and_stripe_session(admin_client, mock_stripe_create):
    """Creating borrowing should create related payment and stripe session."""
    pass

@pytest.mark.django_db
def test_create_borrowing_send_telegram_message(admin_client, mock_send):
    """Creating borrowing should send telegram notification."""
    pass

@pytest.mark.django_db
def test_book_return_increase_inventory(admin_client):
    """Book inventory should be increased by 1"""
    book = BookFactory(inventory=5)
    admin = AdminFactory()

    # Create borrowing and check is it created properly
    payload = {
        "user": admin.id,
        "book": book.id,
        "expected_return_date": (date.today() + timedelta(days=5)).isoformat()
    }

    resp = admin_client.post(BASE, payload, format="json")
    assert resp.status_code == 201
    borrowing_id = resp.data["id"]
    book.refresh_from_db()
    assert book.inventory == 4

    # Return book and checks book's inventory
    resp = admin_client.post(BASE + f"{borrowing_id}/return_book/")
    assert resp.status_code == 200
    book.refresh_from_db()
    assert book.inventory == 5

@pytest.mark.django_db
def test_return_same_book_second_time(auth_client):
    """Can't return same book second time"""
    user = UserFactory()
    book = BookFactory(inventory=2)
    borrowing = Borrowing.objects.create(
        user=user,
        book=book,
        expected_return_date=date.today() + timedelta(days=3),
    )
    # Login user
    auth_client.force_authenticate(user=user)
    # First return should work
    resp1 = auth_client.post(f"{BASE}{borrowing.id}/return_book/")
    borrowing.refresh_from_db()
    book.refresh_from_db()

    assert resp1.status_code == 200
    assert borrowing.actual_return_date == date.today()
    assert book.inventory == 3  # +1

    # Second return attempt should fail
    resp2 = auth_client.post(f"{BASE}{borrowing.id}/return_book/")
    assert resp2.status_code in (400, 403)


@pytest.mark.django_db
def test_actual_return_date_earlier_than_borrow_date(auth_client):
    """Can't set actual_return_date earlier than borrow_date"""
    book = BookFactory()
    user = UserFactory()

    payload = {
        "book": book.id,
        "user": user.id,
        "expected_return_date": (date.today() + timedelta(days=5)).isoformat(),
        "borrow_date": (date.today() + timedelta(days=2)).isoformat()
    }

    auth_client.force_authenticate(user=user)

    resp = auth_client.post(BASE, payload, format="json")
    assert resp.status_code == 201

    borrowing_id = resp.data["id"]
    resp_2 = auth_client.post(BASE + f"{borrowing_id}/return_book/", {"actual_return_date": (date.today() - timedelta(days=1)).isoformat()}, format="json")

    assert resp_2.status_code == 400
    assert resp_2.data["actual_return_date"] == "Return date cannot be earlier than borrow date."


@pytest.mark.django_db
@pytest.mark.parametrize(
    "expected_return_delta, expected_amount, expected_type",
    [
        (-5, Decimal("30.00"), "FINE"), #Overdue
        (5, Decimal("20.00"), "PAYMENT"), #No overdue
    ]
)
def test_money_to_pay(auth_client, expected_return_delta, expected_type, expected_amount):
    """Amount to pay is properly calculated"""
    book = BookFactory(daily_fee="2.00")
    user = UserFactory()
    auth_client.force_authenticate(user=user)

    borrow_date = date.today() - timedelta(days=10)
    expected_return_date = date.today() + timedelta(days=expected_return_delta)
    actual_return_date = date.today()

    payload = {
        "book": book.id,
        "user": user.id,
        "expected_return_date": expected_return_date.isoformat(),
    }

    resp = auth_client.post(BASE, payload, format="json")
    assert resp.status_code == 201
    borrowing_id = resp.data["id"]

    borrowing = Borrowing.objects.get(id=borrowing_id)
    borrowing.borrow_date = borrow_date
    borrowing.save()

    resp_return = auth_client.post(
        BASE + f"{borrowing_id}/return_book/",
        {"actual_return_date": actual_return_date.isoformat()},
        format="json"
    )
    assert resp_return.status_code == 200

    borrowing.refresh_from_db()
    payment = borrowing.payments.first()

    assert payment.money_to_pay == expected_amount
    assert payment.type == expected_type

@pytest.mark.django_db
def test_normal_user_cannot_see_other_user_borrowings(auth_client):
    """Normal user shouldn't be able to see other users borrowings."""
    user1 = UserFactory()
    user2 = UserFactory()

    BorrowingFactory.create_batch(3, user=user1)
    BorrowingFactory.create_batch(2, user=user2)

    auth_client.force_authenticate(user=user1)
    resp = auth_client.get(BASE, {"user_id": user2.id})

    assert resp.status_code == 200
    assert len(resp.data) == 3


@pytest.mark.django_db
def test_admin_user_sees_all_users_borrowings(admin_client):
    """Admin user should see all users borrowings."""
    user1 = UserFactory()
    user2 = UserFactory()
    admin = AdminFactory()

    BorrowingFactory.create_batch(3, user=user1)
    BorrowingFactory.create_batch(2, user=user2)
    BorrowingFactory.create_batch(1, user=admin)

    resp = admin_client.get(BASE)

    assert resp.status_code == 200
    assert len(resp.data) == 6

@pytest.mark.django_db
def test_admin_can_filter_by_is_active(admin_client):
    """Admin user should be able to filter borrowings by is_active param."""
    # Create borrowings
    borrowing_1 = BorrowingFactory()
    borrowing_2 = BorrowingFactory()
    BorrowingFactory()
    BorrowingFactory()

    # Return 2 books
    resp1 = admin_client.post(BASE + f"{borrowing_1.id}/return_book/")
    assert resp1.status_code == 200
    resp2 = admin_client.post(BASE + f"{borrowing_2.id}/return_book/")
    assert resp2.status_code == 200

    # Check list of all borrowings
    resp = admin_client.get(BASE)
    assert resp.status_code == 200
    assert len(resp.data) == 4

    # Check filtered list of borrowings
    resp = admin_client.get(BASE, {"is_active": True})
    assert resp.status_code == 200
    assert len(resp.data) == 2

@pytest.mark.django_db
@pytest.mark.parametrize("has_overdue, called", [
    (True, True),
    (False, False),
])
def test_notify_overdue_borrowings(mock_send, has_overdue, called):
    """Notification should be sent only when there are overdue borrowings."""
    pass