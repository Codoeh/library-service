from decimal import Decimal

from django.db import models

from borrowings.models import Borrowing
from library_service import settings


class Payment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
    ]
    TYPE_CHOICES = [
        ("PAYMENT", "Payment"),
        ("FINE", "Fine"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    session_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True
    )
    session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    money_to_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    def __str__(self):
        if self.money_to_pay > 0:
            return (f"{self.get_type_display()} - "
                    f"{self.status} - {self.money_to_pay} USD")
        return f"{self.get_type_display()} - {self.status} - Nothing to pay"

    def calculate_payment(self):
        borrow = self.borrowing
        actual_return = borrow.actual_return_date
        expected_return = borrow.expected_return_date
        borrow_date = borrow.borrow_date
        daily_fee = Decimal(borrow.book.daily_fee)

        if actual_return is None:
            return Decimal("0.00"), None

        if actual_return <= expected_return:
            total_days = (actual_return - borrow_date).days
            total_days = max(1, total_days)
            total = daily_fee * total_days
            payment_type = "PAYMENT"
        else:
            base_days = (expected_return - borrow_date).days
            base_days = max(1, base_days)
            base_amount = daily_fee * base_days

            delay_days = (actual_return - expected_return).days
            fine_amount = daily_fee * settings.FINE_MULTIPLIER * delay_days

            total = base_amount + fine_amount
            payment_type = "FINE"

        return total, payment_type

    def update_payment_amount(self):
        amount, payment_type = self.calculate_payment()
        self.money_to_pay = amount
        if payment_type:
            self.type = payment_type
        self.save(update_fields=["money_to_pay", "type"])
