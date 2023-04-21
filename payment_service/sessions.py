import stripe

from library_service import settings
from payment_service.models import Payment

stripe.api_key = settings.STRIPE_API_KEY


def create_payment(borrowing, session):
    Payment.objects.create(
        status="PENDING",
        type="PAYMENT",
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=session.amount_total,
    )


def create_payment_session(borrowing):
    days = (borrowing.expected_return_date - borrowing.borrow_date).days
    amount = int(borrowing.book.daily_fee) * days * 100
    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{borrowing.book.title} borrowing for {days} days",
                    },
                    "unit_amount": amount,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://127.0.0.1:8000/api/payments",
        cancel_url="http://127.0.0.1:8000/api/payments",
    )
    create_payment(borrowing, session)
    return session
