from celery import shared_task
from datetime import date
from .models import Borrowing
from utils.telegram_helper import send_telegram_message


@shared_task
def notify_overdue_borrowings():
    overdue = Borrowing.objects.filter(
        expected_return_date__lt=date.today(),
        actual_return_date__isnull=True
    )
    if overdue.exists():
        message = f"Overdue returns - {overdue.count()}:\n"
        for book in overdue:
            message += (f"- {book.book.title} borrowed by"
                        f" {book.user.username}, expected"
                        f" return was {book.expected_return_date}\n")
        send_telegram_message(message)
