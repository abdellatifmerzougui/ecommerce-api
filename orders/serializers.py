from decimal import Decimal

from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field

from products.models import Product
from products.serializers import ProductSerializer

from .models import Cart, CartItem, Order, OrderItem

class CartItemserializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'quantity',
            'subtotal',
        ]
    
    def get_subtotal(self, obj) -> Decimal:
        return obj.product.price * obj.quantity

        

class CartSerializer(serializers.ModelSerializer):
    items = CartItemserializer(many=True,read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart    
        fields = [
            'id',
            'items',
            'created_at',
            'updated_at',
            'total',
        ]

    def get_total(self, obj) -> Decimal:
        total = Decimal('0.00')
        for item in obj.items.all():
            total += item.product.price * item.quantity
        return total


class CartItemCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product')
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = CartItem
        fields = [
            'product_id',
            'quantity',
        ]

    def validate(self, attrs):
        product = attrs['product']
        quantity = attrs['quantity']

        if not product.is_active:
            raise serializers.ValidationError('This product is not available')

        if quantity > product.stock:
            raise serializers.ValidationError(f'Only {product.stock} items are available.')

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data['product']
        quantity = validated_data['quantity']
        cart , _ = Cart.objects.get_or_create(user= user)

        item, created = CartItem.objects.get_or_create(cart=cart,product=product,defaults={'quantity' : quantity})

        if not created:
            new_quantity = item.quantity + quantity

            if new_quantity > product.stock : 
                raise serializers.ValidationError(f'Only {product.stock} items are available.')

            item.quantity = new_quantity
            item.save(update_fields=['quantity'])

        
        return item

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'quantity',
            'price',
            'subtotal',

        ]

    def get_subtotal(self,obj) -> Decimal:
        return obj.price * obj.quantity

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True,read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'items',
            'total',
            'created_at',
            'updated_at',
        ]

class OrderStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['status']

        def validate_status(self,value):
            order = self.instance

            allowed_transitions={
                Order.Status.PENDING: [Order.Status.CONFIRMED,Order.Status.CANCELED],
                Order.Status.CONFIRMED: [Order.Status.SHIPPED],
                Order.Status.SHIPPED: [Order.Status.DELIVERED],
                Order.Status.DELIVERED: [],
                Order.Status.CANCELED: [],
            }
            if value not in allowed_transitions[order.status]:
                raise serializers.ValidationError(f"Can't change order status from {order.status} to {value}")

            return value