from decimal import Decimal

import pytest

from payments.models import Payment
from payments.serializers import PaymentSerializer
from tests.factories import BorrowingFactory


@pytest.mark.django_db
def test_payment_serializer_fields():
    borrowing = BorrowingFactory()
    payment = Payment.objects.create(
        borrowing=borrowing,
        type="PAYMENT",
        money_to_pay=Decimal("5.00")
    )
    serializer = PaymentSerializer(payment)
    data = serializer.data
    assert data["id"] == payment.id
    assert data["money_to_pay"] == "5.00"
    assert data["borrowing_id"] == borrowing.id
    assert data["book_title"] == borrowing.book.title


@pytest.mark.django_db
def test_payment_viewset_success_and_cancel(
        auth_client,
        mock_send_payment_telegram_message,
        mock_stripe_retrieve,
        user
):
    borrowing = BorrowingFactory(user=user)
    payment = Payment.objects.create(
        borrowing=borrowing,
        type="PAYMENT",
        money_to_pay=Decimal("5.00"),
        session_id="sess_123"
    )

    url = f"/api/v1/payments/{payment.id}/success/"
    resp = auth_client.get(url)

    assert resp.status_code == 200
    payment.refresh_from_db()
    assert payment.status == "PAID"
    mock_send_payment_telegram_message.assert_called_once()

    url = f"/api/v1/payments/{payment.id}/cancel/"
    resp = auth_client.get(url)

    assert resp.status_code == 200
    assert resp.data["detail"] == "Payment cancelled"
