from rest_framework import routers

from borrowing_service.views import BorrowingViewSet

router = routers.DefaultRouter()


router.register("", BorrowingViewSet)

urlpatterns = router.urls

app_name = "borrowing_service"
