import datetime

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MinValueValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from tech_shop_app.models import *


class UserProfileSerializer(ModelSerializer):

    def to_representation(self, instance):
        user_repr = super().to_representation(instance)
        user_repr['address'] = instance.profile.address
        user_repr['img_url'] = instance.profile.img_url
        user_repr['phone_number'] = instance.profile.phone_number
        return user_repr

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']


class UserSerializer(ModelSerializer):
    password = serializers.CharField(
        max_length=128, validators=[validate_password], write_only=True)
    address = serializers.CharField(
        required=True, max_length=256, write_only=True
    )
    phone_number = serializers.CharField(
        required=True, max_length=256, write_only=True
    )
    img_url = serializers.URLField(
        required=False, max_length=256, write_only=True
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'address', 'phone_number', 'img_url'
            , 'profile', 'is_staff']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'read_only': True},
        }
        validators = [UniqueTogetherValidator(User.objects.all(), ['email'])]
        depth = 1

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['email'],
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''))
            Profile.objects.create(user=user, address=validated_data['address'],
                                   phone_number=validated_data['phone_number'])
        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number']


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = ProfileUpdateSerializer(many=False)

    class Meta:
        model = User
        fields = ['email', 'profile']

    def update(self, instance, validated_data):
        print(validated_data)
        profile = None
        if 'profile' in validated_data:
            profile = validated_data.pop('profile')
            instance.profile.phone_number = profile['phone_number']
            instance.profile.save()
            print(profile)
        instance.email = validated_data['email']
        instance.save()
        return instance


class DetailedUserSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        fields = '__all__'
        model = Profile


class GetItem(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'price', 'description', 'model', 'category', 'img_url', 'quantity'
            , 'storage', 'color', 'company_name']


class GetAllItems(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'price', 'description', 'model', 'category', 'img_url', 'quantity'
            , 'storage', 'color', 'company_name']


class AddItem(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class GetSavedItems(serializers.ModelSerializer):
    class Meta:
        model = SavedItem
        # fields = ['car']
        fields = []
        depth = 1
        # fields = ['car', 'user']

    def to_representation(self, instance):
        item_instance = instance.item
        item_serializer = GetAllItems(item_instance)
        return item_serializer.data


class AddSavedItem(serializers.ModelSerializer):
    class Meta:
        model = SavedItem
        fields = '__all__'


class GetItemsByCompany(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['price', 'description', 'model', 'category', 'img_url', 'quantity'
            , 'storage', 'color', 'company_name']