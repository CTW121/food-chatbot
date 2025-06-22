from rest_framework import serializers
from .models import Conversation

class ConversationSerializer(serializers.ModelSerializer):
    """
    A serializer class that converts Conversation model instances into JSON-compatible data
    and validates incoming data for creating or updating Conversation objects.
    """
    class Meta:
        """
        The Meta class configures the serializer to work with the Conversation model,
        limiting the serialized data to the specified fields for security and simplicity.
        """
        model = Conversation    # Specifies the Conversation model to serialize
        # fields = ['user_input', 'bot_response', 'is_vegetarian', 'created_at']
        # fields = ['user_input', 'bot_response', 'created_at']
        fields = ['user_input', 'bot_response'] # Specifies the fields to include in the serialized output: user_input and bot_response only