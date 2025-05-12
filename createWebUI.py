# KKey Week 6 Lab: Creating a Web UI

import openai #from openai import OpenAI
import gradio
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Debug: Check if the API key is loaded correctly
print("Loaded .env file:", os.path.exists(".env"))
print("API Key from environment:", os.getenv("OPENAI_API_KEY")) # Ensure the environment variable is set correctly

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY") #client = OpenAI()

# Fallback: Set the API key directly if the environment variable is not loaded
if not openai.api_key:
    openai.api_key = "OPENAI_API_KEY"  # Replace with your actual API key

# Initialize conversation
messages = [{"role": "system", 
             "content": "You are a dog personality expert specializes in type of dog to own."}]

# Define the chatbot function
def CustomChatGPT(user_input):
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply

# Create a Gradio interface
demo = gradio.Interface(fn=CustomChatGPT, inputs="text",
                         outputs="text", title="The Pawfect Dog!",)

# Launch the web interface
demo.launch(share=True)

