from django.db import transaction
from rest_framework import serializers

from book_service.models import Book
from book_service.serializers import BookSerializer
from borrowing_service.models import Borrowing


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )

    def get_user(self, object):
        return object.user.get_full_name() or object.user.username


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )

    def validate(self, attrs):
        if attrs["book"].inventory == 0:
            raise serializers.ValidationError("This book is out of inventory")
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data["book"]
            borrowing = Borrowing.objects.create(**validated_data)
            Book.objects.filter(pk=book.id).update(inventory=book.inventory - 1)
            return borrowing
