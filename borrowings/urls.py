from rest_framework.routers import DefaultRouter
from django.urls import path, include

from borrowings.views import BorrowingViewSet

app_name = "borrowings"

router = DefaultRouter()
router.register(r"", BorrowingViewSet, basename="borrowing")

urlpatterns = [
    path("", include(router.urls)),
]

