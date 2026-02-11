
from rest_framework import viewsets, permissions
from api.models import StorageCredential, ActivityLog
from api.serializers.storage import StorageCredentialSerializer
from api.utils.permissions import IsOwner

class StorageCredentialViewSet(viewsets.ModelViewSet):
    serializer_class = StorageCredentialSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return StorageCredential.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        ActivityLog.objects.create(
            user=self.request.user,
            action_type='settings_update',
            description=f"Added storage credential: {serializer.instance.name}"
        )
