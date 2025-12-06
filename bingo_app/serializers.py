from rest_framework import serializers
from .models import Message, User, VideoCallGroup

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_organizer', 'is_admin']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'content', 'timestamp', 'is_read']

class VideoCallGroupSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = VideoCallGroup
        fields = ['id', 'name', 'created_by', 'is_public', 'agora_channel_name', 'game', 'raffle', 'password', 'created_at']
        read_only_fields = ['agora_channel_name', 'created_at']