
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from api.models import ApiKey, ActivityLog
from api.serializers.apikey import ApiKeySerializer, ApiKeyCreateResponseSerializer
from api.utils.permissions import IsOwner

class ApiKeyViewSet(viewsets.ModelViewSet):
    serializer_class = ApiKeySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return ApiKey.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ApiKeyCreateResponseSerializer
        return ApiKeySerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        ActivityLog.objects.create(
            user=self.request.user,
            action_type='api_key_generated',
            description=f"Generated API Key: {serializer.instance.name}"
        )
