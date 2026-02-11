
from rest_framework import viewsets, permissions
from api.models import ActivityLog
from api.serializers.log import ActivityLogSerializer
from api.utils.permissions import IsOwner

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user)
