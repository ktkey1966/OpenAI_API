# Create "Hello World" program using OpenAI API KKey 4/26/2025

from openai import OpenAI

client = OpenAI(api_key="...")  # Set your OpenAI API key

# Set your OpenAI API key

# Call the OpenAI chat.completions endpoint with gpt-3.5-turbo model
response = client.chat.completions.create(model="gpt-3.5-turbo",
messages=[
    {"role": "user", "content": "Hello, World!"}
])

# Extract and print the response
print(response.choices[0].message.content)