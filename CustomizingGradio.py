# CIS 363 KKey - Week 7 Lab: Creating a Custom Chat Interface using Python, OpenAI's GPT-3 and Gradio

import openai
import gradio as gr
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


# Set your OpenAI API key
openai.api_key = "Your_API_KEY_Here" # Replace with your actual API key

# Initialize conversation history
messages = [{"role": "system", "content": "You are a game show contestant and you have to figure who is the person being described."}]

# Define the chatbot function
def CustomChatbot(user_input, history):
    # Add user input to the conversation history
    messages.append({"role": "user", "content": user_input})
    
    # Call OpenAI's GPT-3.5 model
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    # Extract the chatbot's reply
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    
    # Add the chatbot's reply to the conversation history
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    
    return ChatGPT_reply

# Create the Gradio interface
demo = gr.ChatInterface(
    CustomChatbot,
    chatbot=gr.Chatbot(height=800, type="messages"),
    textbox=gr.Textbox(placeholder="Guess who am I!", container=False, scale=7),
    title="Guess Who Chatbot",
    description="Discribe who you are and what you do.",
    theme="soft",
    examples=["Male or Female", "I buy and sell homes", "Toss a prolate spheroid"],
    cache_examples=False,
    #retry_button=None,
    #undo_btn="Delete Previous",
    #clear_btn="Clear",
)

# Launch the Gradio interface
demo.launch(share=True)