from rest_framework import serializers
from django.core.validators import RegexValidator
from rest_framework.validators import UniqueValidator
from register.models import CustomUser
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.password_validation import validate_password
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(
        validators=[RegexValidator(regex='^[a-zA-Z]*$', message='Only letters are allowed.'),
                    UniqueValidator(queryset=CustomUser.objects.all(), message='This username is already in use.')], required=True
    )
    email = serializers.EmailField(required=True)
    name = serializers.CharField(max_length=20, required=True)
    surname = serializers.CharField(max_length=20, required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'surname', 'email', 'name', 'avatar', 'confirmation_code', "avatar", 'password',
                  'password_confirm', 'created_at', 'is_active']

    def validate_password(self, data):
        if validate_password(data) is not None:
            raise serializers.ValidationError("Password min length is 8")
        return data

    def validate(self, data):

        # Проверяем, что пароли совпадают
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError("Passwords do not match.")

        return data

    def create(self, validated_data):
        confirmation_code = get_random_string(length=4, allowed_chars='0123456789')
        print(confirmation_code)
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            name=validated_data['name'],
            surname=validated_data['surname'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            is_active=False,
            confirmation_code=confirmation_code,
        )

        subject = 'Confirmation code'
        message = f'Your confirmation code is: {confirmation_code}'
        from_email = 'bapaevmyrza038@gmail.com'
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, data):
        if validate_password(data) is not None:
            raise serializers.ValidationError("Password min length is 8")
        return data


class ChangeUsernameSerializer(serializers.Serializer):
    new_username = serializers.CharField(required=True)


class ForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20, required=True)
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    username = serializers.CharField(max_length=20, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, data):
        if validate_password(data) is not None:
            raise serializers.ValidationError("Password min length is 8")
        return data

    def validate(self, data):
        if data.get('new_password') != data.get('confirm_new_password'):
            raise serializers.ValidationError('Passwords is not match')
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'surname', 'email', 'name', 'avatar', 'created_at', 'is_active']


class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username']