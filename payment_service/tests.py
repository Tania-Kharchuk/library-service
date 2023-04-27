from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from book_service.tests import sample_book
from borrowing_service.models import Borrowing
from borrowing_service.tests import sample_borrowing
from payment_service.models import Payment
from payment_service.serializers import PaymentSerializer

PAYMENT_URL = reverse("payment_service:payment-list")


def detail_url(payment_id):
    return reverse("payment_service:payment-detail", args=[payment_id])


class UnauthenticatedPaymentApiTests(TestCase):
    def SetUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PAYMENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test123@test.com",
            "newtestpass",
        )
        borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timedelta(days=10),
            book=sample_book(),
            user=self.user,
        )
        defaults = {
            "status": "PENDING",
            "type": "PAYMENT",
            "borrowing": borrowing,
            "session_url": "http://127.0.0.1:8000/api/payments/",
            "session_id": "some id",
            "money_to_pay": 2.00,
        }
        self.payment = Payment.objects.create(**defaults)
        self.client.force_authenticate(self.user)

    def test_list_payments(self):
        payment1 = self.payment
        payload = {
            "status": "PENDING",
            "type": "PAYMENT",
            "borrowing": sample_borrowing(),
            "session_url": "http://127.0.0.1:8000/api/payments/",
            "session_id": "some id",
            "money_to_pay": 2.00,
        }
        payment2 = Payment.objects.create(**payload)
        res = self.client.get(PAYMENT_URL)

        serializer1 = PaymentSerializer(payment1)
        serializer2 = PaymentSerializer(payment2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_payment_detail(self):
        payment1 = self.payment

        url = detail_url(payment1.id)
        res = self.client.get(url)

        serializer = PaymentSerializer(self.payment)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AdminPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test123@test.com", "newtestpass", is_staff=True
        )
        borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timedelta(days=10),
            book=sample_book(),
            user=self.user,
        )
        defaults = {
            "status": "PENDING",
            "type": "PAYMENT",
            "borrowing": borrowing,
            "session_url": "http://127.0.0.1:8000/api/payments/",
            "session_id": "some id",
            "money_to_pay": 2.00,
        }
        self.payment = Payment.objects.create(**defaults)
        self.client.force_authenticate(self.user)

    def test_list_payments(self):
        payment1 = self.payment
        payload = {
            "status": "PENDING",
            "type": "PAYMENT",
            "borrowing": sample_borrowing(),
            "session_url": "http://127.0.0.1:8000/api/payments/",
            "session_id": "some id",
            "money_to_pay": 2.00,
        }
        payment2 = Payment.objects.create(**payload)
        res = self.client.get(PAYMENT_URL)

        serializer1 = PaymentSerializer(payment1)
        serializer2 = PaymentSerializer(payment2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
