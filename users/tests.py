from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class UserAuthenticationTests(APITestCase):

    def test_register_user(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass123",
            "first_name": "Test",
            "last_name": "User",
        }

        response = self.client.post(
            "/api/users/register/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            User.objects.count(),
            1,
        )

        user = User.objects.get(
            username="testuser"
        )

        self.assertTrue(
            user.check_password("StrongPass123")
        )

    def test_login_user(self):
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass123",
        )

        data = {
            "username": "testuser",
            "password": "StrongPass123",
        }

        response = self.client.post(
            "/api/auth/token/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

        self.assertIn(
            "refresh",
            response.data,
        )

    def test_wrong_password(self):
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass123",
        )

        data = {
            "username": "testuser",
            "password": "WrongPassword",
        }

        response = self.client.post(
            "/api/auth/token/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )