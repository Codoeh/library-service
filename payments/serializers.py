from rest_framework import serializers
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    borrowing_id = serializers.IntegerField(
        source="borrowing.id",
        read_only=True
    )
    book_title = serializers.CharField(
        source="borrowing.book.title",
        read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing_id",
            "session_url",
            "money_to_pay",
            "book_title",
        )
        read_only_fields = ("id",)
