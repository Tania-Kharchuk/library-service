from datetime import datetime, timedelta

import stripe
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from payment.models import Payment
from payment.serializers import PaymentSerializer


class PaymentPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.select_related("borrowing")
    permission_classes = (IsAuthenticated,)
    serializer_class = PaymentSerializer
    pagination_class = PaymentPagination

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing_id__user=self.request.user)

        return queryset

    @action(
        methods=["GET"],
        detail=False,
        url_path="success",
    )
    def success(self, request) -> Response:
        """Success stripe payment endpoint"""
        session_id = request.query_params.get("session_id", False)
        payment = Payment.objects.get(session_id=session_id)
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            serializer = PaymentSerializer(
                payment, data={"status": "PAID"}, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"status": "error", "message": "Payment is not success"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=["GET"],
        detail=False,
        url_path="cancel",
    )
    def cancel(self, request) -> Response:
        """Cancel stripe payment endpoint"""
        session_id = request.query_params.get("session_id")
        payment = Payment.objects.get(session_id=session_id)
        session = stripe.checkout.Session.retrieve(session_id)
        serializer = PaymentSerializer(payment)
        if session.payment_status == "unpaid":
            session_expires_at = datetime.fromtimestamp(session.created) + timedelta(
                hours=24
            )
            time_remaining = session_expires_at - datetime.now()
            message = (
                "Your payment has been cancelled. You can pay later, but please note that the session is "
                f"available for the next {time_remaining}."
            )
            return Response(
                {"message": message, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        message = f"Your payment has been already paid."
        return Response(
            {"message": message, "data": serializer.data},
            status=status.HTTP_200_OK,
        )
