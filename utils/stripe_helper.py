import stripe
from django.urls import reverse
from django.conf import settings


class StripeApiClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.STRIPE_SECRET_KEY
        stripe.api_key = self.api_key

    def create_checkout_session(self, payment, request):
        payment.update_payment_amount()
        amount = int(payment.money_to_pay * 100)

        if amount == 0:
            return payment

        success_url = request.build_absolute_uri(
            reverse("payments:payment-payment-success", kwargs={"pk": payment.id})
        )
        cancel_url = request.build_absolute_uri(
            reverse("payments:payment-payment-cancel", kwargs={"pk": payment.id})
        )

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Library payment for borrowing {payment.borrowing.id}",
                    },
                    "unit_amount": amount,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )

        payment.session_id = session.id
        payment.session_url = session.url
        payment.save(update_fields=["session_id", "session_url"])

        return {"url": session.url}

stripe_client = StripeApiClient()
