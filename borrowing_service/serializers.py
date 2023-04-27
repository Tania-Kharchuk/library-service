from django.db import transaction
from rest_framework import serializers

from book.models import Book
from book.serializers import BookSerializer
from borrowing_service.models import Borrowing
from borrowing_service.notifications import send_telegram_notification
from payment.serializers import PaymentSerializer
from payment.sessions import create_payment_session


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)
    user = serializers.SerializerMethodField()
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )

    def get_user(self, object):
        return object.user.get_full_name() or object.user.username


class BorrowingCreateSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "payments",
        )

    def validate(self, attrs):
        if attrs["book"].inventory == 0:
            raise serializers.ValidationError("This book is out of inventory")
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data["book"]
            borrowing = Borrowing.objects.create(**validated_data)
            create_payment_session(borrowing)
            Book.objects.filter(pk=book.id).update(inventory=book.inventory - 1)
            message = (
                f"New borrowing created:\nUser: {borrowing.user}\n"
                f"Book: {borrowing.book}\nBorrow date: {borrowing.borrow_date}"
            )

            send_telegram_notification(message)
            return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )
        read_only_fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )

    def validate(self, attrs):
        if self.instance.actual_return_date is not None:
            raise serializers.ValidationError("This book is already returned")
        return attrs
