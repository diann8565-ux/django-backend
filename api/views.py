
from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Profile, StorageCredential, Category, File, ActivityLog, ApiKey
from .serializers import (
    ProfileSerializer, StorageCredentialSerializer, CategorySerializer,
    FileSerializer, ActivityLogSerializer, ApiKeySerializer, UserSerializer
)
import uuid
import secrets
import requests
from django.conf import settings

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)
    
    def get_object(self):
        return self.request.user.profile

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data)

class StorageCredentialViewSet(viewsets.ModelViewSet):
    serializer_class = StorageCredentialSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return StorageCredential.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return File.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user)

class ApiKeyViewSet(viewsets.ModelViewSet):
    serializer_class = ApiKeySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return ApiKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Generate sk_... key
        key = f"sk_{secrets.token_urlsafe(32)}"
        serializer.save(user=self.request.user, key=key)

class DevLoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user, created = User.objects.get_or_create(username=email, defaults={'email': email})
        if created:
            user.set_unusable_password()
            user.save()
        
        # Generate JWT manually or use SimpleJWT
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.profile.id,
                'email': user.email,
                'role': user.profile.role
            }
        })

class AIProxyView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        url = "https://one.apprentice.cyou/api/v1/chat/completions"
        try:
            # Forward the request to the external AI service
            response = requests.post(url, json=request.data, headers={'Content-Type': 'application/json'})
            return Response(response.json(), status=response.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HealthCheckView(views.APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({'status': 'ok'})
