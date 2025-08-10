import stripe.checkout
from .models import Payment

def create_stripe_session(borrowing, payment_type):
    payment = Payment.objects.create(
        borrowing=borrowing,
        type=payment_type,
        status="PENDING",
    )

    payment.update_payment_amount()

    amount = int(payment.money_to_pay * 100)
    if amount == 0:
        return payment

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"Library payment for borrowing {borrowing.id}",
                },
                "unit_amount": amount,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="http://localhost:8000/payments/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://localhost:8000/payments/cancel",
    )

    payment.session_id = session.id
    payment.session_url = session.url
    payment.save()

    return payment
