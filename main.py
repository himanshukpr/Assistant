from google import genai
import json
import os
from dotenv import load_dotenv

import platform

operating_system = platform.platform()

load_dotenv()

conversation_history = []


while True:

    user_command  = input('What to do: ')

    conversation_history.append({'role':'user', 'content':user_command})


    client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""user asked {user_command},

        user have asked to do something and you have to answer the query
        and if the user have asked to open something that time you just have to provide the commmand to run in the terminal of the {operating_system},
        and also make sure that if you are giving the command to run in terminal that time the response must not include any single markdown text.
        also if the user is commanding to do something in the system that time you need to just provide the terminal command in such a way that they get executed directly and this response should also not include any type of single markdown content
        but make sure that you are returning the dictionary as the response if response is command that time the result must be, all the following stuructures have to follow strictly:
        "type":"command", "command":"command", "fail_audio":"msg to show if command faild"

        if there is only result as response:
        "type":"response", "content":"content"

        now there is one more condition and that is
        is the user prompt is not starting with the 'mia bhai' or it can me 'miya bhai' but you have to understand 'mia bhai' by default that time it should just say 'Mera name Mia bhai! ha to Mia bhai bhi use kro....' else it  must work normally
        and the response must be in form:
        "type":"response", "content":"content"



        one more condition you are also provided with the all the privious conversation history also and all the history is:
        {conversation_history} so you need to also respond according to that.

        """,
    )

    result = json.loads(response.text)
    conversation_history.append({'role':'system', 'content':result})


    if result['type'] == 'command':
        try:
            os.system(result['command'])
        except:
            print(result['fail_audio'])
        
    else:
        print(result['content'])
        print()