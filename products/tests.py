from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Category, Product


User = get_user_model()


class ProductAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="normaluser",
            email="normal@example.com",
            password="StrongPass123",
        )

        self.staff = User.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="StrongPass123",
            is_staff=True,
        )

        self.category = Category.objects.create(
            name="Electronics",
            slug="electronics",
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Laptop",
            slug="laptop",
            description="Test laptop",
            price="1000.00",
            stock=10,
            is_active=True,
        )

    def test_list_products(self):
        response = self.client.get(
            "/api/products/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_normal_user_cannot_create_product(self):
        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "name": "Mouse",
            "slug": "mouse",
            "description": "Test mouse",
            "price": "50.00",
            "stock": 10,
            "is_active": True,
            "category_id": self.category.id,
        }

        response = self.client.post(
            "/api/products/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_staff_can_create_product(self):
        self.client.force_authenticate(
            user=self.staff
        )

        data = {
            "name": "Mouse",
            "slug": "mouse",
            "description": "Test mouse",
            "price": "50.00",
            "stock": 10,
            "is_active": True,
            "category_id": self.category.id,
        }

        response = self.client.post(
            "/api/products/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_search_products(self):
        response = self.client.get(
            "/api/products/?search=Laptop"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_filter_products_by_category(self):
        response = self.client.get(
            f"/api/products/?category={self.category.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )