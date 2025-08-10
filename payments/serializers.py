from rest_framework.serializers import ModelSerializer
from payments.models import Payment

class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "status", "type", "borrowing", "session_url", "session_id", "money_to_pay",)
        read_only_fields = ("id",)
