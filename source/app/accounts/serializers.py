from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        min_length=3,
        max_length=16,
        validators=[UniqueValidator(queryset=get_user_model().objects.all())])
    email = serializers.EmailField(
        required=True,
        max_length=32,
        validators=[UniqueValidator(queryset=get_user_model().objects.all())])
    password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Password fields didn\'t match.'})
        return attrs

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            is_active=False)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        raise NotImplementedError()


class VerifyEmailSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(required=True, write_only=True)
    token = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        try:
            user_id = urlsafe_base64_decode(attrs['uidb64'])
            user = get_user_model().objects.get(pk=user_id)
            token_check = default_token_generator.check_token(user, attrs['token'])
            if not token_check:
                raise exceptions.ParseError()
        except(KeyError, TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            raise exceptions.ParseError()
        else:
            return {'user_id': user_id, 'is_active': user.is_active, }

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()
