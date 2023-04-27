from datetime import timedelta, datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from book.tests import sample_book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingDetailSerializer,
)
from user.tests import sample_user

BORROWING_URL = reverse("borrowing:borrowing-list")


def sample_borrowing(**params):
    defaults = {
        "expected_return_date": timezone.now() + timedelta(days=10),
        "book": sample_book(),
        "user": sample_user(),
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


def detail_url(borrowing_id):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


def return_url(borrowing_id):
    return reverse("borrowing:return", args=[borrowing_id])


class UnauthenticatedBorrowingApiTests(TestCase):
    def SetUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "newtest@test.com",
            "newtestpass",
        )

        defaults = {
            "expected_return_date": timezone.now() + timedelta(days=10),
            "book": sample_book(),
            "user": self.user,
        }
        self.borrowing = Borrowing.objects.create(**defaults)
        self.client.force_authenticate(self.user)

    def test_list_borrowing(self):
        borrowing1 = sample_borrowing()
        borrowing2 = self.borrowing

        res = self.client.get(BORROWING_URL)

        serializer1 = BorrowingDetailSerializer(borrowing1)
        serializer2 = BorrowingDetailSerializer(borrowing2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer1.data, res.data)

    def test_filter_active_borrowing(self):
        borrowing1 = Borrowing.objects.create(
            expected_return_date=timezone.now() + timedelta(days=10),
            book=sample_book(),
            user=self.user,
        )
        borrowing2 = self.borrowing

        borrowing2.actual_return_date = timezone.now() + timedelta(days=5)

        res = self.client.get(BORROWING_URL, {"is_active": "true"})

        serializer1 = BorrowingDetailSerializer(borrowing1)
        serializer2 = BorrowingDetailSerializer(borrowing2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_borrowing_detail(self):
        url = detail_url(self.borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingDetailSerializer(self.borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self):
        book = Book.objects.create(
            title="Sample book",
            author="Sample author",
            cover="HARD",
            inventory=5,
            daily_fee=2.00,
        )
        payload = {
            "expected_return_date": timezone.now() + timedelta(days=10),
            "book": book.id,
        }

        res_create = self.client.post(BORROWING_URL, payload)
        borrowing = Borrowing.objects.get(id=res_create.data["id"])
        url = detail_url(borrowing.id)
        res_retrieve = self.client.get(url)
        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(borrowing.book.inventory, 4)
        self.assertEqual(res_retrieve.data, serializer.data)

    def test_create_borrowing_with_0_book_inventory(self):
        book = Book.objects.create(
            title="Sample book",
            author="Sample author",
            cover="HARD",
            inventory=0,
            daily_fee=2.00,
        )
        payload = {
            "expected_return_date": timezone.now() + timedelta(days=10),
            "book": book.id,
        }

        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_borrowing(self):
        url = detail_url(self.borrowing.id)
        res_retrieve = self.client.get(url)
        res_return = self.client.post(return_url(self.borrowing.id))
        res_retrieve_after_return = self.client.get(url)
        return_date_str = res_retrieve_after_return.data["actual_return_date"]
        actual_return_date = datetime.fromisoformat(return_date_str[:-1])

        self.assertEqual(res_retrieve.data["actual_return_date"], None)
        self.assertEqual(res_return.status_code, status.HTTP_200_OK)
        self.assertEqual(
            actual_return_date.date(),
            timezone.now().date(),
        )
        self.assertEqual(
            res_retrieve_after_return.data["book"]["inventory"],
            res_retrieve.data["book"]["inventory"] + 1,
        )

    def test_return_borrowing_twice(self):
        res_return = self.client.post(return_url(self.borrowing.id))
        res_return_twice = self.client.post(return_url(self.borrowing.id))

        self.assertEqual(res_return_twice.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            res_return_twice.data["non_field_errors"][0],
            "This book is already returned",
        )


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com", "testpass", is_staff=True
        )
        defaults = {
            "expected_return_date": timezone.now() + timedelta(days=10),
            "book": sample_book(),
            "user": self.user,
        }
        self.borrowing = Borrowing.objects.create(**defaults)
        self.client.force_authenticate(self.user)

    def test_filter_borrowing_by_user(self):
        borrowing1 = Borrowing.objects.create(
            expected_return_date=timezone.now() + timedelta(days=10),
            book=sample_book(),
            user=sample_user(),
        )
        borrowing2 = self.borrowing

        res = self.client.get(BORROWING_URL, {"user_id": borrowing1.user_id})

        serializer1 = BorrowingDetailSerializer(borrowing1)
        serializer2 = BorrowingDetailSerializer(borrowing2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
