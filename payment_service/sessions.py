import stripe

from borrowing_service.models import Borrowing
from library_service import settings
from payment_service.models import Payment

stripe.api_key = settings.STRIPE_API_KEY
FINE_MULTIPLIER = 2


def create_payment(
    borrowing: Borrowing, session: stripe.checkout.Session, payment_type: str
) -> None:
    Payment.objects.create(
        status="PENDING",
        type=payment_type,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=session.amount_total,
    )


def create_payment_session(
    borrowing: Borrowing, days: int = None
) -> stripe.checkout.Session:
    if days:
        amount = int(borrowing.book.daily_fee) * days * 100 * FINE_MULTIPLIER
        payment_type = "FINE"
    else:
        days = (borrowing.expected_return_date - borrowing.borrow_date).days
        amount = int(borrowing.book.daily_fee) * days * 100
        payment_type = "PAYMENT"
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
    create_payment(borrowing, session, payment_type)
    return session
