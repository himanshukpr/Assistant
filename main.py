from google import genai
import json
import os
from dotenv import load_dotenv

import speech_recognition as sr

import platform

operating_system = platform.platform()

load_dotenv()



while True:

    user_command  = input('What to do: ')

    client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""user asked {user_command},
        user have asked to do something and you have to answer the query 
        and if the user have asked to open something that time you just have to provide the commmand to run in the terminal of the {operating_system},
        and also make sure that if you are giving the command to run in terminal that time the response must not include any single markdown text.
        also if the user is commanding to do something in the system that time you need to just provide the terminal command in such a way that they get executed directly and this response should also not include any type of single markdown content
        but make sure that you are retuning the dictoniry as the response if response is command that time the result must be:
        "type":"command", "content":"content", "fail_audio":"msg to show if command faild"

        if there is only result as response:
        "type":"response", "content":"content"
        
        """,
    )

    result = json.loads(response.text)

    if result['type'] == 'command':
        try:
            os.system(result['content'])
            
        except:
            print(result['fail_audio'])
        
    else:
        print(result['content'])