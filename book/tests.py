from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from book.serializers import BookSerializer

BOOK_URL = reverse("book:book-list")


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Sample author",
        "cover": "HARD",
        "inventory": 5,
        "daily_fee": 2.00,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(book_id):
    return reverse("book:book-detail", args=[book_id])


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_book(self):
        sample_book(title="title1")
        sample_book(title="title2")

        res = self.client.get(BOOK_URL)

        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_detail(self):
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_permissions(self):
        payload = {
            "title": "Sample book",
            "author": "Sample author",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 2.00,
        }
        book = sample_book()
        url = detail_url(book.id)
        res_create = self.client.post(BOOK_URL, payload)
        res_destroy = self.client.delete(url)
        res_update = self.client.put(url, payload)
        res_partial_update = self.client.patch(url, data={"title": "new"})
        responses = [res_create, res_destroy, res_update, res_partial_update]

        for res in responses:
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_book(self):
        sample_book(title="title1")
        sample_book(title="title2")

        res = self.client.get(BOOK_URL)

        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_detail(self):
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_permissions(self):
        payload = {
            "title": "Sample book",
            "author": "Sample author",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 2.00,
        }
        book = sample_book()
        url = detail_url(book.id)
        res_create = self.client.post(BOOK_URL, payload)
        res_destroy = self.client.delete(url)
        res_update = self.client.put(url, payload)
        res_partial_update = self.client.patch(url, data={"title": "new"})
        responses = [res_create, res_destroy, res_update, res_partial_update]

        for res in responses:
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "Sample book",
            "author": "Sample author",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 2.00,
        }

        res_create = self.client.post(BOOK_URL, payload)
        book = Book.objects.get(id=res_create.data["id"])

        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(book, key))

    def test_delete_book(self):
        book = sample_book()
        url = detail_url(book.id)
        res_destroy = self.client.delete(url)
        deleted_book = Book.objects.filter(id=book.id)
        self.assertEqual(res_destroy.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(deleted_book.count(), 0)

    def test_update_book(self):
        payload = {
            "title": "Sample book",
            "author": "Sample author",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 2.00,
        }
        book = sample_book()
        url = detail_url(book.id)
        res_update = self.client.put(url, data=payload)
        updated_book = Book.objects.get(id=res_update.data["id"])
        for key in payload:
            self.assertEqual(payload[key], getattr(updated_book, key))
        res_partial_update = self.client.patch(url, data={"title": "new"})
        partial_updated_book = Book.objects.get(id=res_update.data["id"])

        self.assertEqual(partial_updated_book.title, "new")
        self.assertEqual(res_partial_update.status_code, status.HTTP_200_OK)
        self.assertEqual(res_update.status_code, status.HTTP_200_OK)
