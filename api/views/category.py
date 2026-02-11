
from rest_framework import viewsets, permissions
from api.models import Category, ActivityLog
from api.serializers.category import CategorySerializer
from api.utils.permissions import IsOwner

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        ActivityLog.objects.create(
            user=self.request.user,
            action_type='create_category',
            description=f"Created category: {serializer.instance.name}"
        )
