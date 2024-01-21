 
import os 
import openai 

openai.api_key=os.environ.get("OPENAI_API_KEY")

#Takes in context messages, returns generated response
async def generate_response(message):  
    try: 
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message
        )  
        return str(completion.choices[0].message.content)
        
    except Exception as e:
        print(f"Error during OpenAI API request: {e}") 
 