
from rest_framework import serializers
from api.models import ApiKey

class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = [
            'id', 'name', 'prefix', 'last_used_at', 
            'expires_at', 'is_active', 'scopes', 'created_at'
        ]
        read_only_fields = ['id', 'prefix', 'last_used_at', 'created_at']

    def create(self, validated_data):
        raise serializers.ValidationError("API Key generation disabled. Use ENV.")
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Only show full key on creation if we were passing it back, 
        # but here we are not hashing yet so it's stored in DB.
        # In this implementation we don't return the full key in list view for security, 
        # but maybe on create we should return it.
        return data

class ApiKeyCreateResponseSerializer(ApiKeySerializer):
    class Meta(ApiKeySerializer.Meta):
        fields = ApiKeySerializer.Meta.fields
