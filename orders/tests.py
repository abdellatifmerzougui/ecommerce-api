from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from decimal import Decimal
from products.models import Category, Product

from .models import Cart, CartItem, Order, OrderItem


User = get_user_model()


class CartAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="cartuser",
            email="cart@example.com",
            password="StrongPass123",
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

        self.client.force_authenticate(
            user=self.user
        )

    def test_get_empty_cart(self):
        response = self.client.get(
            "/api/cart/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["items"],
            [],
        )

        self.assertEqual(
            response.data["total"],
            0,
        )

    def test_add_product_to_cart(self):
        data = {
            "product_id": self.product.id,
            "quantity": 2,
        }

        response = self.client.post(
            "/api/cart/items/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        item = CartItem.objects.get(
            product=self.product
        )

        self.assertEqual(
            item.quantity,
            2,
        )

    def test_add_same_product_increases_quantity(self):
        CartItem.objects.create(
            cart=Cart.objects.create(
                user=self.user
            ),
            product=self.product,
            quantity=2,
        )

        data = {
            "product_id": self.product.id,
            "quantity": 3,
        }

        response = self.client.post(
            "/api/cart/items/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        item = CartItem.objects.get(
            product=self.product
        )

        self.assertEqual(
            item.quantity,
            5,
        )

    def test_cannot_add_more_than_stock(self):
        data = {
            "product_id": self.product.id,
            "quantity": 11,
        }

        response = self.client.post(
            "/api/cart/items/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class CheckoutAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="checkoutuser",
            email="checkout@example.com",
            password="StrongPass123",
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

        self.client.force_authenticate(
            user=self.user
        )

        self.cart = Cart.objects.create(
            user=self.user
        )

        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

    def test_checkout_creates_order(self):
        response = self.client.post(
            "/api/orders/checkout/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get(
            user=self.user
        )

        self.assertEqual(
            order.total,
            Decimal("2000.00"),
        )

        self.assertEqual(
            order.items.count(),
            1,
        )

    def test_checkout_reduces_stock(self):
        self.client.post(
            "/api/orders/checkout/",
            {},
            format="json",
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            8,
        )

    def test_checkout_clears_cart(self):
        self.client.post(
            "/api/orders/checkout/",
            {},
            format="json",
        )

        self.assertEqual(
            CartItem.objects.filter(
                cart=self.cart
            ).count(),
            0,
        )

    def test_order_item_keeps_purchase_price(self):
        self.client.post(
            "/api/orders/checkout/",
            {},
            format="json",
        )

        order_item = OrderItem.objects.get(
            order__user=self.user
        )

        self.assertEqual(
            order_item.price,
            Decimal("1000.00"),
        )

    def test_user_can_only_see_own_orders(self):
        self.client.post(
            "/api/orders/checkout/",
            {},
            format="json",
        )

        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="StrongPass123",
        )

        other_order = Order.objects.create(
            user=other_user,
            status=Order.Status.PENDING,
            total="500.00",
        )

        response = self.client.get(
            f"/api/orders/{other_order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )