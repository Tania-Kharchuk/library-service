from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from payment.sessions import create_payment_session


class BorrowingPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingDetailSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = BorrowingPagination

    def get_queryset(self):
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        queryset = self.queryset

        if is_active == "true":
            queryset = queryset.filter(actual_return_date__isnull=True)

        if user_id and self.request.user.is_staff:
            queryset = queryset.filter(user_id=int(user_id))

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer

        return BorrowingDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
    )
    def return_book(self, request, pk):
        """Return borrowed book"""
        with transaction.atomic():
            borrowing = get_object_or_404(Borrowing, id=pk)
            serializer = BorrowingReturnSerializer(
                borrowing, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            borrowing.actual_return_date = timezone.now()
            borrowing.save()
            if borrowing.actual_return_date > borrowing.expected_return_date:
                days = (
                    borrowing.actual_return_date.date()
                    - borrowing.expected_return_date.date()
                ).days
                create_payment_session(borrowing, days)
            book = borrowing.book
            book.inventory += 1
            book.save()
            serializer.save()
            response_serializer = BorrowingDetailSerializer(borrowing)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.BOOL,
                description="Filter by active borrowings (ex. ?is_active=true)",
            ),
            OpenApiParameter(
                "user_id",
                type=OpenApiTypes.INT,
                description="Filter by user_id (ex. ?user_id=2)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


# class BorrowingReturnView(APIView):
#     permission_classes = (IsAuthenticated,)
#
#     @extend_schema(
#         responses={200: BorrowingDetailSerializer},
#         methods=["POST"],
#     )
#     def post(self, request, pk):
#         """Return borrowed book"""
#         with transaction.atomic():
#             borrowing = get_object_or_404(Borrowing, id=pk)
#             serializer = BorrowingReturnSerializer(
#                 borrowing, data=request.data, partial=True
#             )
#             serializer.is_valid(raise_exception=True)
#             borrowing.actual_return_date = timezone.now()
#             borrowing.save()
#             if borrowing.actual_return_date > borrowing.expected_return_date:
#                 days = (
#                     borrowing.actual_return_date.date()
#                     - borrowing.expected_return_date.date()
#                 ).days
#                 create_payment_session(borrowing, days)
#             book = borrowing.book
#             book.inventory += 1
#             book.save()
#             serializer.save()
#             response_serializer = BorrowingDetailSerializer(borrowing)
#             return Response(response_serializer.data, status=status.HTTP_200_OK)
