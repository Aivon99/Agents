from google import genai
import requests
import json
import os 
from LLM_API_List import API_List

import threading


'''
OLLAMA_URL = "http://localhost:11434/api/generate"


def call_ollama():
    payload = {
        "model": "llama3.2",
        "prompt": "Hello, how are you?",
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    print(response.json())

''' 


# the purpose of this is to only use the free tier level,
# round robin approach
# some APIs give multiple models, 
# I don't expect to run out of tokens either way so Imma use only the most powerful models available (at least at this stage)
   
class LLMQuery():
    lock = threading.Lock()  # Class-level lock, trying not to cause probles when using multiple instances

    def __init__(self):
        self.current_index = 0
        
    def get_next_api():
        global current_index

        with LLMQuery.lock:            
            
            # pretty ugly but it's life and it's midnight 
            SelectedAPI = API_List[list(API_List.keys())[current_index]]

            # Extract desired components
            api_url = SelectedAPI["URL"]
            APIKey = SelectedAPI["Key"]
            model = SelectedAPI["Model"]

            current_index = (current_index + 1) % len(API_List)
        print("calling : ", list(API_List.keys())[current_index], " with model: ",  model)
        return list(API_List.keys())[current_index], api_url, APIKey, model
    
    @staticmethod
    
    def format_payload(api_name, Payload): #Obviously not all APIs want the payload in the same format, would have been too easy
    
        if api_name == "google":
            return None # Google API is handled separately in the query_google_ai function 
        
        elif api_name == "cohere":
            return {
        "model": "mistral-small-latest",
        "temperature": 1.5,
        "top_p": 1,
        "max_tokens": 0,
        "stream": false,
        "stop": "string",
        "random_seed": 0,
        "messages": [
            {
            "role": "user",
            "content": "Who is the best French painter? Answer in one short sentence."
            }
        ],
        "response_format": {
            "type": "text",
            "json_schema": {
            "name": "string",
            "description": "string",
            "schema": {},
            "strict": false
            }
        },
        "tools": [
            {
            "type": "function",
            "function": {
                "name": "string",
                "description": "",
                "strict": false,
                "parameters": {}
            }
            }
        ],
        "tool_choice": "auto",
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "n": 1,
        "prediction": {
            "type": "content",
            "content": ""
        },
        "parallel_tool_calls": true,
        "safe_prompt": false
        }
        
        elif api_name == "huggingface":
            return {"inputs": None, "parameters": {"max_tokens": None}}
        
        elif api_name == "open_source":
            return {"model": None, "prompt": None, "max_tokens": None}
        elif api_name == "local":
            return {"model": None, "prompt": None, "max_tokens": None}
        else:
            raise ValueError("Unknown API format")

    def run_api_query(api_url, api_key, model, Payload):
        
        
        try:
            response = requests.post(api_url, json=data, headers=headers)
            response.raise_for_status()  # Raises an exception for HTTP errors
            result = response.json()
            return result  # Or customize this to return only the desired part of the response
        except requests.RequestException as e:
            print(f"API Request failed: {e}")
            return None
        
    
    
    def __call__(self, Payload):
     
        api_name, api_url, api_key, model = self.get_next_api()
        
        formatted_payload = self.format_payload(api_name, Payload) #assuming Payload contains all relevant info 
        try:
            if(api_name == "Google_AI_Studio"):
                answer = queryGemini(formatted_payload, api_key, model)
            else:
                answer = self.run_api_query(api_url, api_key, model, formatted_payload)
            return answer
        
        except requests.RequestException as e:
            print(f"API Request failed: {e}")
            return None
        
def queryGemini(Payload, api_key, model):

    client = genai.Client(api_key= api_key)
    response = client.models.generate_content(
        model = model,
        contents=Payload,
    )
    return response
    
'''
Payload variable expected structure: 

'''

