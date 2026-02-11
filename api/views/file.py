
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models import File, Category, ActivityLog
from api.serializers.file import FileSerializer
from api.serializers.category import CategorySerializer
from api.utils.permissions import IsOwner

class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filterset_fields = ['file_type', 'is_favorite']
    search_fields = ['name']

    def get_queryset(self):
        queryset = File.objects.filter(user=self.request.user).select_related('storage_account').prefetch_related('categories')
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        # Trigger external deletion logic here via service if needed
        ActivityLog.objects.create(
            user=self.request.user, 
            action_type='delete', 
            description=f"Deleted file: {instance.name}"
        )
        instance.delete()

    @action(detail=True, methods=['get'])
    def categories(self, request, pk=None):
        file = self.get_object()
        serializer = CategorySerializer(file.categories.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def set_categories(self, request, pk=None):
        file = self.get_object()
        category_ids = request.data.get('category_ids', [])
        categories = Category.objects.filter(id__in=category_ids, user=request.user)
        file.categories.set(categories)
        
        ActivityLog.objects.create(
            user=request.user, 
            action_type='update', 
            description=f"Updated categories for file: {file.name}"
        )
        
        return Response({'status': 'categories updated'})
