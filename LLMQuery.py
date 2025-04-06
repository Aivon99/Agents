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

        return api_url, APIKey, model
    
    @staticmethod
    
    def format_payload(api_config, prompt, token_limit): #Obviously not all APIs want the payload in the same format, would have been too easy
    
        if api_config["Format"] == "google":
            return {"model": api_config["Model"], "input": prompt, "parameters": {"max_tokens": token_limit}}
        
        elif api_config["Format"] == "cohere":
            return {"model": api_config["Model"], "prompt": prompt, "max_tokens": token_limit}
        
        elif api_config["Format"] == "huggingface":
            return {"inputs": prompt, "parameters": {"max_tokens": token_limit}}
        
        elif api_config["Format"] == "open_source":
            return {"model": api_config["Model"], "prompt": prompt, "max_tokens": token_limit}
        else:
            raise ValueError("Unknown API format")

    def run_api_query(api_url, api_key, model, tokenLimit, prompt):
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        if tokenLimit is None:
            data = {
                "model": model,
                "prompt": prompt,
            }
        else:
            data = {
                "model": model,
                "prompt": prompt,
                "max_tokens": tokenLimit  
            }
        
        try:
            response = requests.post(api_url, json=data, headers=headers)
            response.raise_for_status()  # Raises an exception for HTTP errors
            result = response.json()
            return result  # Or customize this to return only the desired part of the response
        except requests.RequestException as e:
            print(f"API Request failed: {e}")
            return None
        
    
    
    def __call__(self, prompt, tokenLimit):
     
        api_url, api_key, model = self.get_next_api()
        answer = self.run_api_query(api_url, api_key, model, tokenLimit prompt)
        
        return answer
    

def query_google_ai(prompt, googleAPI):
    url = f"https://generativelanguage.googleapis.com/v1beta2/models/{googleAPI['Model']}:generateText"
    headers = {
        "Authorization": f"Bearer {googleAPI['API_Key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": {"text": prompt},
        "temperature": 0.7,
        "maxOutputTokens": 512
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["candidates"][0]["output"]
    else:
        return f"Error {response.status_code}: {response.json().get('error', {}).get('message', 'Unknown error')}"



def queryGemini(prompt, googleAPI):

    client = genai.Client(api_key= googleAPI["API_Key"] )
    response = client.models.generate_content(
        model = googleAPI["Model"],
        contents=prompt,
    )
    return response
    

