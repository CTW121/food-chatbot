from django.shortcuts import render
from django.http import JsonResponse
import openai
from django.conf import settings
from .models import Conversation
import json
import re

# Create your views here.
openai.api_key = settings.OPENAI_API_KEY # Use key from  settings

def chatbot(request):
    if request.method == "POST":
        user_input = request.POST.get("user_input", "").strip()
        prompt = (f"You are friendly chatbot. Ask the user: 'What are your top 3 favorite foods?' \
        If they respond, thank them and list their foods (e.g., '1. food1, 2. food2, 3. food3'). \
        If they don't  provide foods or the list is incomplete, gently prompt again. User said: {user_input}")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )

        bot_response = response.choices[0].message.content.strip()
        foods = []
        if user_input and any(str(i) in user_input for i in range(1,4)):
            # Extract foods if numbered list is detected
            food_matches = re.findall(r'(?:\d+\.|-)\s*([^\d\n]+)', bot_response)
            foods = [food.strip() for food in food_matches[:3]]
        if foods and len(foods) == 3:
            Conversation.objects.create(
                user_input=user_input,
                bot_response=bot_response,
                favorite_foods=json.dumps(foods),
                is_vegetarian=check_vegetarian(foods)
            )
        else:
            bot_response = "Thanks for your input! Please provide exactly 3 favorite foods \
            (e.g., '1. pizza, 2. pasta, 3. salad') for me to process."
        return JsonResponse({"response": bot_response})
    return render(request, 'chatbot.html', {"initial_message": "Welcome! Please enter your top 3 favorite foods."})

def check_vegetarian(foods):
    non_veg_keywords = ["chicken", "beef", "pork", "fish", "shrimp", "lamb", "turkey", "duck", "venison", "goat",
                        "rabbit", "veal", "bacon", "sausage", "ham", "salami", "prosciutto", "crab", "lobster",
                        "squid", "octopus", "clams", "mussels", "oysters", "scallops", "gelatin", "broth", "stock",
                        "lard", "suet", "tallow", "meat", "seafood", "poultry", "game"]

    for food in foods:
        food_lower = food.lower()
        if any(keyword in food_lower for keyword in non_veg_keywords):
            return False
    return True