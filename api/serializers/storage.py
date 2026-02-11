
from rest_framework import serializers
from api.models import StorageCredential

class StorageCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageCredential
        fields = [
            'id', 'name', 'provider', 'public_key', 'url_endpoint',
            'region', 'bucket_name', 'is_active', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'private_key_encrypted': {'write_only': True}
        }
    
    def create(self, validated_data):
        # In a real app, encrypt private key here
        return super().create(validated_data)
