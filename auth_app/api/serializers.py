from rest_framework import serializers
from django.contrib.auth.models import User

from auth_app.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["user", "fullname"]


class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True, required=True, error_messages={
        "required": "fullname is required."})
    email = serializers.EmailField(write_only=True, required=True, error_messages={
        "required": "Email is required."})
    password = serializers.CharField(write_only=True, required=True, error_messages={
        "required": "Password is required."})
    repeated_password = serializers.CharField(write_only=True, required=True, error_messages={
        "required": "Please confirm your password."
    })

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def save(self,  **kwargs):
        account = User(
            email=self.validated_data["email"], username=self.validated_data["email"])

        account.set_password(self.validated_data["password"])
        account.save()

        UserProfile.objects.create(
            user=account,
            fullname=self.validated_data["fullname"]
        )

        return account


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=True, error_messages={
        "required": "Email is required."})
    password = serializers.CharField(write_only=True, required=True, error_messages={
        "required": "Password is required."
    })
