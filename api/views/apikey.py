
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from api.models import ApiKey, ActivityLog
from api.serializers.apikey import ApiKeySerializer
from api.utils.permissions import IsOwner

class ApiKeyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ApiKeySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return ApiKey.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        return Response({'detail': 'API Key generation disabled. Use ENV.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'API Key deletion disabled. Use ENV.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
