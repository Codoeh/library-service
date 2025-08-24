from django.db import models


class Book(models.Model):
    COVER_CHOICES = [
        ("HARD", "Hardcover"),
        ("SOFT", "Softcover"),
    ]
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.CharField(max_length=4, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return (f"{self.title} written by {self.author} in {self.cover}. "
                f"On inventory: {self.inventory}."
                f" Daily fee: {self.daily_fee} $USD.")
