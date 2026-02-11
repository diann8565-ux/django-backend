
from rest_framework import serializers
from api.models import Category

class CategorySerializer(serializers.ModelSerializer):
    file_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'color', 'icon', 'description', 
            'sort_order', 'parent', 'file_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'file_count']

    def validate_color(self, value):
        if not value.startswith('#'):
            raise serializers.ValidationError("Color must be a hex code starting with #")
        return value
