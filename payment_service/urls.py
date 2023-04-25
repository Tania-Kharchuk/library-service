from rest_framework import routers
from django.urls import path, include

from payment_service.views import PaymentViewSet

router = routers.DefaultRouter()


router.register("", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("success/", PaymentViewSet.as_view({"get": "success"}), name="success"),
    path("cancel/", PaymentViewSet.as_view({"get": "cancel"}), name="cancel"),
]

app_name = "payment_service"
