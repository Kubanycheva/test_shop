from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

from django.contrib.auth.views import LogoutView
from .serializers import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', ]
        extra_kwargs = {'password': {'write_only': True}}

        def create(self, validated_data):
            user = User.objects.create_user(**validated_data)
            return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Неверные учетные данные')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name']

class UserProfileSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']


class ProductPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhotos
        fields = ['image']


class RatingSerializer(serializers.ModelSerializer):
    user = UserProfileSimpleSerializer()

    class Meta:
        model = Rating
        fields = ['user', 'stars']


class ReviewSerializer(serializers.ModelSerializer):
    author = UserProfileSimpleSerializer()
    created_date = serializers.DateTimeField('%d-%m-%Y %H:%M')

    class Meta:
        model = Review
        fields = ['author', 'text', 'parent_review', 'created_date']


class ProductListSerializers(serializers.ModelSerializer):
    product = ProductPhotosSerializer(read_only=True, many=True)
    category = CategorySerializer()
    reviews = ReviewSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    date = serializers.DateField(format='%d-%m-%Y')
    owner = UserProfileSimpleSerializer()



    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product', 'category', 'price', 'date',
                  'ratings', 'reviews', 'owner']





class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    reviews = ReviewSerializer(read_only=True, many=True)
    ratings = RatingSerializer(read_only=True, many=True)
    product = ProductPhotosSerializer(read_only=True, many=True)
    average_rating = serializers.SerializerMethodField()
    date = serializers.DateField('%d-%m-%Y')

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'category', 'description', 'product', 'product_video',
                  'price', 'average_rating', 'active', 'ratings', 'reviews', 'date']
    def get_average_rating(self, obj):
        return obj.get_average_rating()


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='product')

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'get_total_price' ]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()

