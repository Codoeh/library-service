from rest_framework.routers import DefaultRouter
from django.urls import path, include

from borrowings.views import BorrowingViewSet

router = DefaultRouter()
router.register(r"", BorrowingViewSet, basename="borrowing")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "borrowings"
