import stripe.checkout
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from library_service.permissions import IsAdminOrIfAuthenticatedReadOnly
from payments.models import Payment
from payments.serializers import PaymentSerializer
from utils.telegram_helper import send_telegram_message


class PaymentViewSet(ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = Payment.objects.all().select_related(
            "borrowing",
            "borrowing__book",
            "borrowing__user"
        )
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            queryset = queryset.filter(borrowing__user=user)
        return queryset

    @extend_schema(
        description="Mark payment as successful if Stripe confirms payment.",
        responses={
            200: OpenApiResponse(description="Payment successful"),
        },
        parameters=[
            OpenApiParameter(
                name="pk",
                description="ID of the payment",
                required=True,
                type=int,
            )
        ]
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="success",
        url_name="payment-success"
    )
    def payment_success(self, request, pk=None):
        payment = get_object_or_404(Payment, pk=pk)

        if payment.session_id:
            session = stripe.checkout.Session.retrieve(payment.session_id)
            if session.payment_status == "paid":
                payment.status = "PAID"
                payment.save(update_fields=["status"])
                send_telegram_message(
                    f"Payment successful: {payment.money_to_pay} "
                    f"$USD for borrowing: {payment.borrowing.id}")
                return Response(
                    {"detail": "Payment successful"},
                    status=status.HTTP_200_OK
                )
        return Response(
            {"detail": "Payment not confirmed"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        description="Cancel the payment (no actual Stripe interaction).",
        responses={
            200: OpenApiResponse(description="Payment cancelled")
        },
        parameters=[OpenApiParameter(
            name="pk",
            description="ID of the payment",
            required=True,
            type=int,
        )]
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="cancel",
        url_name="payment-cancel"
    )
    def payment_cancel(self, request, pk=None):
        return Response(
            {"detail": "Payment cancelled"},
            status=status.HTTP_200_OK
        )
