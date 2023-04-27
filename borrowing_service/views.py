from rest_framework import viewsets, mixins

from borrowing_service.models import Borrowing
from borrowing_service.serializers import BorrowingDetailSerializer


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingDetailSerializer
