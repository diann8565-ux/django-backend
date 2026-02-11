
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, StorageCredential, Category, File, ActivityLog, ApiKey

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'full_name', 'avatar_url', 'role', 'created_at', 'updated_at']

class StorageCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageCredential
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

class FileSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, write_only=True, source='categories', required=False
    )

    class Meta:
        model = File
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = '__all__'
        read_only_fields = ['user', 'key', 'created_at', 'updated_at', 'last_used_at']
