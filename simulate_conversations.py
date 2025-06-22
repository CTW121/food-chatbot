import os
import django
import openai
import random
import time
from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_chatbot.settings')
django.setup()
application = get_wsgi_application()

from chatbot.models import Conversation

# Clear all previous conversations
Conversation.objects.all().delete()

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def chatgpt_a_ask():
    """
    Generates a simple prompt for the ChatGPT model to ask the user about their favorite foods.

    :return: A string containing the prompt "What are your top 3 favorite foods? Please keep the description short and simple."
    """
    return "What are your top 3 favorite foods? Please keep the description short and simple."

def chatgpt_b_respond():
    """
    Generates a response from a simulated food enthusiast by randomly selecting three foods
    and validating the response using the OpenAI API to ensure a natural and enthusiastic output.

    :return: A string containing a natural language response listing the top 3 favorite foods
    :raises: Exception if the OpenAI API call fails (e.g., invalid key or network issue)
    """
    foods = [
        "pizza", "chicken", "beef", "salad", "tofu", "lentils", "pasta", "rice",
        "broccoli", "carrots", "spinach", "quinoa", "eggs", "fish", "shrimp", "turkey",
        "avocado", "cheese", "bread", "beans", "potatoes", "sweet potatoes", "mushrooms",
        "cucumber", "tomatoes", "oranges", "apples", "bananas", "berries", "yogurt", "oats",
        "peanut butter", "almonds", "cashews", "walnuts", "hummus", "zucchini", "cauliflower",
        "brussels sprouts", "asparagus", "onions", "garlic", "peppers", "corn", "peas",
        "cabbage", "eggplant", "pineapple", "grapes", "melon", "cherries", "kiwi",
        "mango", "papaya", "coconut", "figs", "dates", "raisins", "cranberries", "blueberries",
        "sardines", "salmon", "tuna", "duck", "pork", "bacon", "sausages", "lamb",
        "barley", "millet", "couscous", "bulgur", "buckwheat", "noodles", "gnocchi",
        "tortilla", "pita", "bagel", "croissant", "pancakes", "waffles", "cereal",
        "milk", "cream", "butter", "ice cream", "gelato", "chocolate", "jam", "honey",
        "maple syrup", "soy milk", "almond milk", "coconut milk", "chia seeds", "flax seeds",
        "sunflower seeds", "pumpkin seeds", "tempeh", "seitan", "clams", "scallops", "lobster"
    ]
    random.shuffle(foods)
    top_3 = foods[:3]

    # Validate with OpenAI to ensure a natural response
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a food enthusiast. "
                                          "List your top 3 favorite foods based on the suggestion."},
            {"role": "user", "content": f"Suggest: {', '.join(top_3)}"}
        ],
        max_tokens=200  # Allows up to 200 tokens for a detailed and natural response
    )
    return response.choices[0].message.content.strip() # Returns the cleaned AI-generated response listing the top 3 foods

# Simulate 100 conversations
results = []
for i in range(100):
    # Loops 100 times to simulate multiple conversations
    question = chatgpt_a_ask()
    answer = chatgpt_b_respond()
    conversation = Conversation.objects.create(user_input=question, bot_response=answer)
    results.append({"iteration": i+1, "question": question, "answer": answer})
    print(f"Iteration {i+1}: Question: {question}, Answer: {answer}")
    time.sleep(1) # Rate limit respect; pauses execution for 1 second to avoid overwhelming the API or database

with open("conversation_results.txt", "w") as f:
    # Opens a file to write the simulation results
    for result in results:
        f.write(f"Iteration: {result['iteration']}\nQuestion: {result['question']}\nAnswer: {result['answer']}\n------\n")

print(f"Completed 100 simulations. Results saved to conversation_results.txt")