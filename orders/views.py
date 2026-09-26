from django.shortcuts import get_object_or_404
from django.db import transaction

from decimal import Decimal

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import CartItem, Cart, Order, OrderItem
from .serializers import CartItemCreateSerializer,CartItemserializer, CartSerializer, OrderSerializer, OrderItemSerializer, OrderStatusSerializer
from .permissions import IsStaff

# Create your views here.

class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes=[IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return Cart.objects.prefetch_related('items__product__category','items__product__images').get(pk=cart.pk)

class CartItemCreateView(generics.CreateAPIView):
    serializer_class = CartItemCreateSerializer
    permission_classes = [IsAuthenticated]

class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemserializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def parform_update(self, serializer):
        product = serializer.instance.product
        quantity = serializer.validated_data['quantity']

        if not product.is_active:
            raise ValidationError('This product is not available.')

        if quantity>product.stock:
            raise ValidationError(f'Only {product.stock} item are availible.')

        serializer.save()

class CheckoutView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        cart = Cart.objects.select_for_update().filter(user=request.user).first()

        if not cart:
            raise ValidationError("Cart does not exist.")

        cart_items = list(CartItem.objects.select_related("product").select_for_update().filter(cart=cart))

        if not cart_items : 
            raise ValidationError("Your cart is empty.")

        order = Order.objects.create(user= request.user,status=Order.Status.PENDING,total=Decimal("0.00"))
        total = Decimal("0.00")

        for cart_item in cart_items:
            product = Product.objects.select_for_update().get(pk=cart_item.product_id)
            if not product.is_active:
                raise ValidationError(f"{product.name} is not available.")

            if cart_item.quantity > product.stock:
                raise ValidationError(f"Only {product.stock} items of {product.name} are available.")

            price = product.price
            subtotal = price * cart_item.quantity

            OrderItem.objects.create(order=order,product=product,quantity= cart_item.quantity,price=price)
            total += subtotal

            product.stock -= cart_item.quantity

            product.save(update_fields=['stock'])

        order.total = total
        order.save(update_fields=["total"])

        cart_item_qs = CartItem.objects.filter(cart=cart)
        cart_item_qs.delete()

        serializer = OrderSerializer(order,context={'request':request})
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.none()

    def get_queryset(self):
        if getattr(self,"swagger_fake_view",False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product__category","items__product__images").order_by("-created_at")

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.none()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product__category","items__products__images")
       
    
    
class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializer
    permission_classes = [IsStaff]
    http_method_names = ['patch']
    