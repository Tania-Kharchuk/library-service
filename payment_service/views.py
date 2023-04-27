from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from payment_service.models import Payment
from payment_service.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("borrowing")
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing_id__user=self.request.user)

        return queryset
