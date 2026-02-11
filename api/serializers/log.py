
from rest_framework import serializers
from api.models import ActivityLog

class ActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user_email', 'action_type', 'description', 
            'details', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'user_email', 'created_at']
