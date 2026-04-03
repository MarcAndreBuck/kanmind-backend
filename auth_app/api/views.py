from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegistrationSerializer


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

        return Response(serializer.errors, status=400)
    

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
            
            return Response({"error": "Invalid email or password"}, status=400)
        
        return Response(serializer.errors, status=400)