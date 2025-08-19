import factory
from django.contrib.auth import get_user_model

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda  n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_staff = False


class AdminFactory(UserFactory):
    is_staff = True


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Sequence(lambda n: f"Book {n}")
    author = "John Doe"
    cover = "HARD"
    inventory = 5
    daily_fee = "1.50"


class BorrowingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Borrowing

    user = factory.SubFactory(UserFactory)
    book = factory.SubFactory(BookFactory)
    borrow_date = factory.Faker("date_this_year")
    expected_return_date = factory.Faker("date_this_year")


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    borrowing = factory.SubFactory(BorrowingFactory)
    status = "PENDING"
    type = "PAYMENT"
    session_url = None
    session_id = None
