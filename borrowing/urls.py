from rest_framework import routers
from django.urls import path, include

from borrowing.views import BorrowingViewSet

router = routers.DefaultRouter()


router.register("", BorrowingViewSet)

urlpatterns = [
    path(
        "<int:pk>/return",
        BorrowingViewSet.as_view({"post": "return_book"}),
        name="return",
    ),
    path("", include(router.urls)),
]

app_name = "borrowing"
