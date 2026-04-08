from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from kanban_app.api.permissions import IsBoardOwnerMemberOrAdmin

from .serializers import EmailCheckResponseSerializer, EmailCheckSerializer, LoginSerializer, RegistrationSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()

            token, created = Token.objects.get_or_create(user=saved_account)

            return Response({
                "token": token.key,
                "fullname": saved_account.profile.fullname,
                "email": saved_account.email,
                "user_id": saved_account.id
            }, status=201)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            user = authenticate(username=email, password=password)

            if user is not None:
                token, created = Token.objects.get_or_create(user=user)

                return Response({
                    "token": token.key,
                    "fullname": user.profile.fullname,
                    "email": user.email,
                    "user_id": user.id
                }, status=200)

            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated, IsBoardOwnerMemberOrAdmin]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"detail": "Logout successful. Token has been deleted."}, status=status.HTTP_200_OK)


class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = EmailCheckSerializer(data=request.query_params)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Email not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        response_serializer = EmailCheckResponseSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
