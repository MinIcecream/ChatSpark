 
import os 
import openai
from dotenv import load_dotenv  

load_dotenv()
openai.api_key=os.getenv("OPENAI_API_KEY")

 
async def generate_response(message): 
     
    try: 
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message
        )  
        return str(completion.choices[0].message.content)
        
    except Exception as e:
        print(f"Error during OpenAI API request: {e}") 
 