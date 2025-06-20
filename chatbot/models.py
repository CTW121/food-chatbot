from django.db import models
import json

# Create your models here.
class Conversation(models.Model):
    user_input = models.TextField()
    bot_response = models.TextField()
    favorite_foods = models.TextField() # JSON string of food list
    is_vegetarian = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_food(self):
        return json.loads(self.favorite_foods)