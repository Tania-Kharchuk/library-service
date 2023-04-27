from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.serializers import UserSerializer

USER_CREATE_URL = reverse("user:create")
USER_MANAGE_URL = reverse("user:manage")


def sample_user(**params):
    defaults = {
        "email": "sample@gmail.com",
        "first_name": "Sample name",
        "last_name": "Sample last name",
        "password": "testpass",
    }
    defaults.update(params)

    return get_user_model().objects.create(**defaults)


class UnauthenticatedUserApiTests(TestCase):
    def SetUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(USER_MANAGE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user(self):
        payload = {
            "email": "sample@gmail.com",
            "first_name": "Sample name",
            "last_name": "Sample last name",
            "password": "testpass",
        }

        res_create = self.client.post(USER_CREATE_URL, payload)
        user = get_user_model().objects.get(id=res_create.data["id"])

        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.email, "sample@gmail.com")


class AuthenticatedUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_manage_user(self):
        user1 = sample_user()

        res = self.client.get(USER_MANAGE_URL)
        serializer = UserSerializer(self.user)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertNotEqual(res.data["email"], user1.email)
