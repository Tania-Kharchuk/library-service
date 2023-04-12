from rest_framework import serializers

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
