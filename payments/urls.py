from rest_framework.routers import DefaultRouter

from payments.views import PaymentViewSet


app_name = "payments"

router = DefaultRouter()
router.register(r"", PaymentViewSet, basename="payment")

urlpatterns = router.urls
