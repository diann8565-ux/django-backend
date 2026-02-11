
from rest_framework import serializers
from api.models import File, Category
from .category import CategorySerializer

class FileSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, write_only=True, source='categories', required=False
    )
    size_formatted = serializers.CharField(read_only=True)

    class Meta:
        model = File
        fields = [
            'id', 'name', 'original_name', 'url', 'thumbnail_url', 
            'file_type', 'extension', 'size', 'size_formatted',
            'file_id', 'folder_path', 'storage_account',
            'categories', 'category_ids', 'tags', 
            'is_favorite', 'is_public', 
            'download_count', 'last_accessed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'size_formatted', 
            'download_count', 'last_accessed_at'
        ]

    def create(self, validated_data):
        # Additional logic if needed during creation
        return super().create(validated_data)
