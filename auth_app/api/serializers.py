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
        """Validate that the email is unique.

        Checks if a user with the given email already exists.
        Raises ValidationError if email is already in use.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate(self, attrs):
        """Validate the registration data.

        Ensures that password and repeated_password match.
        Raises ValidationError if passwords do not match.
        """
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def save(self,  **kwargs):
        """Create and save a new user account with profile.

        Creates a User instance with email and password.
        Also creates a UserProfile with the fullname.
        Returns the created User instance.
        """
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


class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class EmailCheckResponseSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        """Return the full name from the user's profile.

        Retrieves the fullname field from the associated UserProfile.
        Used for serializing user data with full name.
        """
        return obj.profile.fullname
