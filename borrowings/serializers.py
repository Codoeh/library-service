from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from borrowings.models import Borrowing
from payments.stripe_helper import create_stripe_session
from payments.models import Payment

class BorrowingSerializer(ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book", "user")
        read_only_fields = ("id",)

    def create(self, validated_data):
        validated_data.pop("actual_return_date", None)
        with transaction.atomic():
            book = validated_data.get("book")
            if book.inventory <= 0:
                raise ValidationError("Book is out of stock.")
            book.inventory -= 1
            book.save()
            borrowing = Borrowing.objects.create(**validated_data)

            payment = Payment.objects.create(borrowing=borrowing)
            payment.update_payment_amount()
            stripe_session = create_stripe_session(payment)
            if isinstance(stripe_session, dict) and "url" in stripe_session:
                payment.session_url = stripe_session["url"]
            payment.save(update_fields=["session_url"])

            return borrowing

    def update(self, instance, validated_data):
        with transaction.atomic():
            actual_return_date = validated_data.get("actual_return_date")
            if actual_return_date:
                if instance.actual_return_date is not None:
                    raise ValidationError("This borrowing has already been returned.")
                if actual_return_date < instance.borrow_date:
                    raise ValidationError("Return date cannot be earlier than borrow date.")

                book = instance.book
                book.inventory += 1
                book.save()

                instance.actual_return_date = actual_return_date
                instance.save(update_fields=["actual_return_date", "book"])

                payment = Payment.objects.create(borrowing=instance)
                payment.update_payment_amount()

                stripe_session = create_stripe_session(payment)
                if isinstance(stripe_session, dict) and "url" in stripe_session:
                    payment.session_url = stripe_session["url"]
                    payment.save(update_fields=["session_url"])
                self.context["created_payment"] = payment
                return instance

        return super().update(instance, validated_data)
