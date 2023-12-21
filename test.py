 
import os 
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key=os.getenv("OPENAI_API_KEY")
#openai-env\Scripts\activate
#source openai-env/bin/activate
messages=[{"role": "system", "content": "You are to return a conversation starter based on the messages you're given. Only return the conversation starter. Make it relevent to the conversation."}]

 
while True:
  user_input=input("Say something: ")

  if user_input=='exit':
    print("exiting program.")
    break

  messages.append({"role": "user", "content": user_input})


completion = openai.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=messages
)
 
print(completion.choices[0].message)