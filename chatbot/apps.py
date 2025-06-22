from django.apps import AppConfig

class ChatbotConfig(AppConfig):
    """
    This class is a configuration for the chatbot Django app, inheriting from AppConfig,
    and is used by Django to initialize the app, including setting the default auto field
    for model primary keys and identifying the app name during project setup.
    """
    default_auto_field = "django.db.models.BigAutoField" # Specifies the default auto-incrementing primary key field type as a 64-bit integer for models in the chatbot app
    name = "chatbot" # Defines the name of the application as 'chatbot' for Django to recognize and load it