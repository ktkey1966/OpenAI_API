#CIS363 Alternative Assignment Lab 4 Kevin Key 4/30/2025

from openai import OpenAI

client = OpenAI()

#Call the openai ChatCompletion endpoint
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system", "content": "You are a basball player."
        },
        {
            "role": "user", "content": "My name is Slugger Smith.",
        },
        {
            "role": "assistant", "content": "Hello Slugger Smith. Do you want to play catch?",
        },
        {
            "role": "user", "content": "Where is my glove?",
        },
    ],  
)

#Extract the response
print(response.choices[0].message.content)  