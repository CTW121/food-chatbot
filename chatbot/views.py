from django.shortcuts import render
from django.http import JsonResponse
import openai
from django.conf import settings
import json
import re
import os
from dotenv import load_dotenv
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Conversation
from .serializers import ConversationSerializer

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create your views here.
load_dotenv()
openai.api_key = settings.OPENAI_API_KEY # Use key from  settings

def chatbot(request):
    """
    Handles the chatbot interaction, processing user input via POST requests and returning a bot response.
    If the input contains a valid list of 3 favorite foods, it saves the conversation to the database.
    Otherwise, it prompts the user to provide a complete list.

    :param request: The HTTP request object, expected to contain user_input in POST data
    :return: A JsonResponse with the bot's response or a rendered HTML page for GET requests
    """
    if request.method == "POST":
        user_input = request.POST.get("user_input", "").strip()
        prompt = (f"You are friendly chatbot. Ask the user: 'What are your top 3 favorite foods?' \
        If they respond, thank them and list their foods (e.g., '1. food1, 2. food2, 3. food3'). \
        If they don't  provide foods or the list is incomplete, gently prompt again. User said: {user_input}")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Specifies the OpenAI model to use for generating responses
            messages=[{"role": "user", "content": prompt}], # Sends the prompt to the model
            max_tokens=150  # Limits the response length to 150 tokens
        )

        bot_response = response.choices[0].message.content.strip()  # Extracts the bot's response from the API call
        foods = []
        if user_input and any(str(i) in user_input for i in range(1,4)):
            # Checks if user input contains numbered items (1-3)
            # Extract foods if numbered list is detected
            food_matches = re.findall(r'(?:\d+\.|-)\s*([^\d\n]+)', bot_response)
            foods = [food.strip() for food in food_matches[:3]] # Limits to top 3 foods and cleans them
        if foods and len(foods) == 3:
            # Validates that exactly 3 foods were extracted
            Conversation.objects.create(
                user_input=user_input,  # Saves the user's input
                bot_response=bot_response,  # Saves the bot's response
                favorite_foods=json.dumps(foods),   # Converts the foods list to a JSON string for storage
                is_vegetarian=check_vegetarian(foods)   # Determines if the foods are vegetarian using a custom function
            )
        else:
            bot_response = "Thanks for your input! Please provide exactly 3 favorite foods \
            (e.g., '1. pizza, 2. pasta, 3. salad') for me to process."  # Prompts user for correct input
        return JsonResponse({"response": bot_response}) # Returns the bot's response as JSON
    return render(request, 'chatbot.html', {"initial_message": "Welcome! Please enter your top 3 favorite foods."}) # Renders the chatbot HTML page with an initial message for GET requests

def check_vegetarian(foods):
    """
    Determines if a list of foods is vegetarian by checking against a set of non-vegetarian keywords.

    :param foods: A list of food items to evaluate
    :return: Boolean indicating whether all foods are vegetarian (True) or contain non-vegetarian items (False)
    """
    non_veg_keywords = ["chicken", "beef", "pork", "fish", "shrimp", "lamb", "turkey", "duck", "venison", "goat",
                        "rabbit", "veal", "bacon", "sausage", "ham", "salami", "prosciutto", "crab", "lobster",
                        "squid", "octopus", "clams", "mussels", "oysters", "scallops", "gelatin", "broth", "stock",
                        "lard", "suet", "tallow", "meat", "seafood", "poultry", "game"]

    for food in foods:
        food_lower = food.lower()
        if any(keyword in food_lower for keyword in non_veg_keywords):
            # Checks if any non-vegetarian keyword is present in the food
            return False
    return True

def simulate_conversation(request):
    """
    Simulates 100 conversations by repeatedly asking an AI model for the user's top 3 favorite foods
    and collects the responses for analysis or testing purposes.

    :param request: The HTTP request object, expected to be a POST request to trigger the simulation
    :return: A JsonResponse containing a list of dictionaries with iteration number, question, and AI response

    Note: This function assumes a POST request; other methods (e.g., GET) are not handled and will result in no response
    """
    if request.method == "POST":
        results = []
        for i in range(100):
            question = "What are your top 3 favorite foods?"
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": question}],
                max_tokens=100
            )
            answers = response.choices[0].message.content.strip()
            results.append({"iteration": i+1, "question": question, "answer": answer})
        return JsonResponse({"results": results})

@api_view(['GET'])
def vegetarian_users_api(request):
    """
    API endpoint to retrieve a list of users classified as vegetarian or vegan based on their favorite foods.
    Uses OpenAI to classify conversation responses and returns the results in a JSON format.

    :param request: The HTTP GET request object, authenticated via Basic Authentication
    :return: A Response object containing two lists: 'vegetarian_users' and 'vegan_users' with serialized data
    :raises: HTTP 500 if OpenAI API call or serialization fails
    """
    # Define vegetarian/vegan foods
    vegetarian_foods = {'tofu', 'salad', 'lentils', 'pasta', 'rice', 'vegetables', 'mango', 'kiwi', 'chia', 'bulgur', 'corn'}
    non_vegetarian_foods = {'chicken', 'beef', 'pork', 'fish', 'meat'}
    non_vegan_foods = {'eggs', 'dairy', 'cheese', 'milk', 'butter', 'honey', 'cream'}

    conversations = Conversation.objects.all()
    logger.info(f"Conversations: {conversations}")

    vegetarian_list = []
    vegan_list = []
    for conv in conversations:
        logger.info(f"Processing: {conv.bot_response}")
        # Use OpenAI to classify
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Analyze the following list of favorite foods and determine if it is vegetarian, vegan, or neither. Respond strictly only 'vegetarian', 'vegan', or 'neither'."},
                {"role": "user", "content": conv.bot_response}
            ],
            max_tokens=10,  # Limits the response to 10 tokens for efficiency
            temperature = 0 # Sets temperature to 0 for deterministic output
        )
        classification = response.choices[0].message.content.strip().lower()
        logger.info(f"Classification for {conv.bot_response}: {classification}")

        # if hasattr(conv, 'is_vegetarian'):
        #     conv.is_vegetarian = classification in ['vegetarian', 'vegan']
        #     conv.save()

        serializer = ConversationSerializer(conv)   # Serializes the conversation object
        data = serializer.data  # Gets the serialized data
        data['classification'] = classification # Adds the classification to the serialized data
        if classification == 'vegetarian':
            vegetarian_list.append(data)
        elif classification == 'vegan':
            vegan_list.append(data)

    return Response({"vegetarian_users": vegetarian_list, "vegan_users": vegan_list})