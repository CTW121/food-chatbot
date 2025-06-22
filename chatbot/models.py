from django.db import models
import json

# Create your models here.
class Conversation(models.Model):
    user_input = models.TextField() # Stores the user's input text for the conversation
    bot_response = models.TextField()   # Stores the bot's response text to the user's input
    favorite_foods = models.TextField() # JSON string of food list representing the user's favorite foods
    is_vegetarian = models.BooleanField(default=False)  # Boolean flag indicating if the user is vegetarian, defaults to False
    created_at = models.DateTimeField(auto_now_add=True)    # Automatically sets the date and time when the conversation record is created

    def get_food(self):
        """
        Retrieves the favorite foods stored as a JSON string and converts it into a Python data structure.

        :return: A Python list or dictionary representing the user's favorite foods, parsed from the JSON string in favorite_foods.
        """
        return json.loads(self.favorite_foods) # Parses and returns the JSON string of favorite_foods as a Python list or dictionary