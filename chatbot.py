 
import os 
import openai
from dotenv import load_dotenv
import threading

load_dotenv()
openai.api_key=os.getenv("OPENAI_API_KEY")
#venv\Scripts\activate
#source venv/bin/activate
#messages=[{"role": "system", "content": "You are to return a conversation starter based on the messages you're given. Only return the #conversation starter. Make it relevent to the conversation."}]


# while True:
#   user_input=input("Say something: ")

#   if user_input=='exit':
#     print("exiting program.")
#     break

#   messages.append({"role": "user", "content": user_input})


# completion = openai.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=messages
# )

async def generate_response(messages):
    print("GENERATING")
    try: 
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        ) 
        print("ChatGPT Response: " + str(completion.choices[0].message.content))
    except Exception as e:
        print(f"Error during OpenAI API request: {e}")
    return completion.choices[0].message
