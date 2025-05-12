# CIS 363 KKey 5/8/25
# Week 5 Lab: Creating a Chatbot with Conversation History 


from openai import OpenAI

client = OpenAI()

message = ""
messages = []
system_msg = input("What type of fanbot would you like to create?\n")
messages.append({"role": "system", "content": system_msg})

print("\nYour new number 1 fan is ready!")
print("Start by typing a message and pressing enter. To quit, type STOP\n")
while message != "STOP":
    message = input("You: ")
    if message == "STOP":
        break
    else:
        messages.append({"role": "user", "content": message})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages)
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        print("\nBOT: " + reply + "\n")
print("Chatbot Session Ended")
