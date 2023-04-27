from rest_framework import routers
from django.urls import path, include

from borrowing.views import BorrowingViewSet, BorrowingReturnView

router = routers.DefaultRouter()


router.register("", BorrowingViewSet)

urlpatterns = [
    path("<int:pk>/return", BorrowingReturnView.as_view(), name="return"),
    path("", include(router.urls)),
]

app_name = "borrowing"
