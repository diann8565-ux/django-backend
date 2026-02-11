
from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'full_name', 'avatar_url', 'role', 'bio', 
            'phone_number', 'is_verified', 'preferences', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'role', 'is_verified']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['full_name', 'avatar_url', 'bio', 'phone_number', 'preferences']
