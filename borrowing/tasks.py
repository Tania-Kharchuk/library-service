import datetime

from borrowing.models import Borrowing

from celery import shared_task

from borrowing.notifications import send_telegram_notification


@shared_task
def notification_about_overdue_borrowings():
    today = datetime.datetime.now()
    queryset = Borrowing.objects.filter(
        actual_return_date__isnull=True, expected_return_date__lt=today
    )
    if not queryset:
        send_telegram_notification("No borrowings overdue today!")
    else:
        for borrowing_overdue in queryset:
            message = (
                f"This borrowing is overdue:\nUser: {borrowing_overdue.user}\n"
                f"Book: {borrowing_overdue.book}\nBorrow date: {borrowing_overdue.borrow_date}\n"
                f"Expected return date: {borrowing_overdue.expected_return_date}"
            )
            send_telegram_notification(message)
