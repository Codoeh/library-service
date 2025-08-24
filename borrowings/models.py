from django.db import models
from rest_framework.exceptions import ValidationError

from books.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    def clean(self):
        if self.actual_return_date:
            if self.actual_return_date < self.borrow_date:
                raise ValidationError(
                    {"actual_return_date": "Return date cannot "
                                           "be earlier than borrow date."}
                )
            if self.pk and Borrowing.objects.filter(
                    pk=self.pk,
                    actual_return_date__isnull=False
            ).exists():
                raise ValidationError(
                    {"actual_return_date": "This borrowing has "
                                           "already been returned."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (f"{self.book.title} borrowed by {self.user.username}"
                f"at {self.borrow_date}")
