 
import os 
import openai 
import database_interface as db

openai.api_key=os.environ.get("OPENAI_API_KEY")

input_str="You are given a conversation in the format speaker:message. Return a message for guest 1 to continue the conversation. DO NOT INCLUDE ANY VARIATIONS OF guest 1: IN YOUR RESPONSE. ONLY THE MESSAGE, NO GUEST 1. KEEP THE MESSGE UNDER 10 WORDS. IT MUST BE SHORT."
#Takes in context messages, returns generated response
async def generate_response(client):  
    try: 
        messages=[{"role":"system","content":input_str}]

        for rows in db.get_user_messages(client):
            message=rows[0]
            new_message={"role":"user","content":message}
            messages.append(new_message)

        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )  
        return str(completion.choices[0].message.content)
        
    except Exception as e:
        print(f"Error during OpenAI API request: {e}") 
 