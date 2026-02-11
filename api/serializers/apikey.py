
from rest_framework import serializers
from api.models import ApiKey
import secrets

class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = [
            'id', 'name', 'prefix', 'last_used_at', 
            'expires_at', 'is_active', 'scopes', 'created_at'
        ]
        read_only_fields = ['id', 'prefix', 'last_used_at', 'created_at']

    def create(self, validated_data):
        # Generate a secure random key
        raw_key = secrets.token_urlsafe(32)
        key_string = f"sk_{raw_key}"
        validated_data['key'] = key_string # In real app, hash this
        validated_data['prefix'] = key_string[:7]
        return super().create(validated_data)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Only show full key on creation if we were passing it back, 
        # but here we are not hashing yet so it's stored in DB.
        # In this implementation we don't return the full key in list view for security, 
        # but maybe on create we should return it.
        return data

class ApiKeyCreateResponseSerializer(ApiKeySerializer):
    key = serializers.CharField(read_only=True)
    
    class Meta(ApiKeySerializer.Meta):
        fields = ApiKeySerializer.Meta.fields + ['key']
