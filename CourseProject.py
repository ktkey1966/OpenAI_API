# KKey CIS 363 6/14/2025 Week 10 Lab: Build a Multi-Functional OpenAI-based Application using DALL-E and Gradio


# Required Libraries:
# pip install openai
# pip install gradio
# pip install requests
# pip install pillow

import os
import signal
import sys
import gradio as gr
import requests
from PIL import Image
from io import BytesIO
from openai import OpenAI

# Instantiate the new OpenAI client
client = OpenAI(api_key=os.getenv("YOUR_OPENAI_API_KEY_HERE"))

# -----------------------------
# Signal Handler for Graceful Shutdown
# -----------------------------
def signal_handler(sig, frame):
    print("Interrupt received, shutting down gracefully...")
    try:
        demo.close()
    except Exception:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# -----------------------------
# 1. Function to Generate Text with GPT-3.5
# -----------------------------
def openai_create(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.9,
        max_tokens=1020,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6
    )
    return response.choices[0].message.content.strip()

# -----------------------------
# 2. Function to Simulate a Chatbot
# -----------------------------
def chatgpt_clone(user_input, state):
    if state is None:
        state = []
    # Build API message list with system message, conversation state, and new input.
    messages_for_api = [{"role": "system", "content": """You are a snobbish artist, who thinks all art except your own
                                                is amateurish."""}]+ state + [{"role": "user", "content": user_input}]
    output = openai_create(messages_for_api)
    # Update state as a list of dictionaries.
    state.append({"role": "user", "content": user_input})
    state.append({"role": "assistant", "content": output})
    return state, state

# -----------------------------
# 3. Create the Chatbot UI
# -----------------------------
text_block = gr.Blocks()

with text_block:
    gr.Markdown("""<h1><center>My ChatbotGPT</center></h1>""")
    # Gradio's Chatbot component now expects messages in dictionary format, so explicitly set type.
    chatbot = gr.Chatbot(type="messages")
    messages_box = gr.Textbox(placeholder="Type your message here:")
    state = gr.State()  # Will store conversation history
    send_button = gr.Button("SEND")
    send_button.click(chatgpt_clone, inputs=[messages_box, state], outputs=[chatbot, state])

# -----------------------------
# 4. Functions and UI for DALL-E
# -----------------------------
def openai_create_img(prompt):
    response = client.images.generate(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    r = requests.get(image_url, stream=True)
    img = Image.open(r.raw)
    return img

img_block = gr.Blocks()
with img_block:
    gr.Markdown("""<h1><center>My DALL-E</center></h1>""")
    new_image = gr.Image()
    image_prompt = gr.Textbox(placeholder="Enter an image prompt:")
    send_img_btn = gr.Button("SEND")
    send_img_btn.click(openai_create_img, inputs=[image_prompt], outputs=[new_image])

def openai_var_img(im):
    # Ensure the input is a PIL Image.
    if not isinstance(im, Image.Image):
        im = Image.fromarray(im)
    im = im.resize((1024, 1024))
    im.save("img1.png", "PNG")
    # Use the create_variation endpoint to generate an image variation.
    response = client.images.create_variation(
        image=open("img1.png", "rb"),
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    r = requests.get(image_url, stream=True)
    img = Image.open(r.raw)
    return img

img_var_block = gr.Blocks()
with img_var_block:
    gr.Markdown("""<h1><center>DALL-E Image Variator</center></h1>""")
    with gr.Row():
        im_input = gr.Image(label="Input Image")
        im_output = gr.Image(label="Varied Image")
    send_var_btn = gr.Button("SEND")
    send_var_btn.click(openai_var_img, inputs=[im_input], outputs=[im_output])

# -----------------------------
# 5. Launch the Gradio Interface
# -----------------------------
demo = gr.TabbedInterface(
    [text_block, img_block, img_var_block],
    ["My ChatbotGPT", "My DALL-E", "DALL-E Image Variator"]
)

if __name__ == "__main__":
    demo.launch(share=True)





