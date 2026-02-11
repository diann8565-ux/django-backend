
from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from api.serializers.auth import LoginSerializer, ChangePasswordSerializer, DevLoginSerializer
from api.models import ActivityLog

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add extra responses here
        data['user'] = {
            'id': self.user.profile.id,
            'email': self.user.email,
            'role': self.user.profile.role,
            'full_name': self.user.profile.full_name,
            'avatar_url': self.user.profile.avatar_url
        }
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
             # Log login
            try:
                user = User.objects.get(email=request.data.get('email') or request.data.get('username'))
                ActivityLog.objects.create(user=user, action_type='login', description="User Login via Password")
            except:
                pass
        return response

class DevLoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = DevLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user, created = User.objects.get_or_create(username=email, defaults={'email': email})
            if created:
                user.set_unusable_password()
                user.save()
            
            refresh = RefreshToken.for_user(user)
            
            # Log login
            ActivityLog.objects.create(user=user, action_type='login', description="Developer Login")

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.profile.id,
                    'email': user.email,
                    'role': user.profile.role,
                    'full_name': user.profile.full_name,
                    'avatar_url': user.profile.avatar_url
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            ActivityLog.objects.create(user=user, action_type='settings_update', description="Changed Password")
            
            return Response({"status": "password set"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
