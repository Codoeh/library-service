from celery import shared_task
from datetime import date
from .models import Borrowing
from utils.telegram_helper import send_telegram_message

@shared_task
def notify_overdue_borrowings():
    overdue = Borrowing.objects.filter(return_date__lt=date.today(), returned=False)
    if overdue.exists():
        message = f"Overdue returns - {overdue.count()}:\n"
        for book in overdue:
            message += f"- {book.book.title} borrowed by {book.user.username}, return was {book.return_date}\n"
        send_telegram_message(message)