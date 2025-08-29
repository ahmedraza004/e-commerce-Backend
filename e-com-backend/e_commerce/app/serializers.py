from rest_framework import serializers
from .models import Product, Cart, CartItem, Order,Category
from django.contrib.auth.models import User


# class 
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def validate_email(self, value):
     if User.objects.filter(email=value).exists():
        raise serializers.ValidationError("Email already in use")
     return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# category serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model= Category
        fields= ['id','name','description']


# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    image = serializers.ImageField(use_url=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='Category', write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'image','category','category_id']  # Replace with actual fields

# Cart Item Serializer
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id','cart','product', 'product_id', 'quantity']
 # Add 'quantity' if applicable

# Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source= "cart_items",many=True, read_only=True)  # 'items' must match related_name in CartItem

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']  # Include 'user' if Cart is user-specific

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    cart = CartSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'cart', 'status', 'created_at']  # Add timestamps if needed