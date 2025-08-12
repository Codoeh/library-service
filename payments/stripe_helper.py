import stripe
from .models import Payment

def create_stripe_session(payment):
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
                    "name": f"Library payment for borrowing {payment.borrowing.id}",
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
    payment.save(update_fields=["session_id", "session_url"])

    return {"url": session.url}
