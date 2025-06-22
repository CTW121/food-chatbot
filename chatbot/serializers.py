from rest_framework import serializers
from .models import Conversation

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['user_input', 'bot_response', 'is_vegetarian', 'created_at']
        # fields = ['user_input', 'bot_response']