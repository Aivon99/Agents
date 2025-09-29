from google import genai
import requests
import json
import os 
import time
from collections import deque
import threading

from LLM_API_List import API_List


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
# the purpose of this is to only use the free tier level, piicking models based on type of the task
# semi round robin approach
class LeakyBucketLimiter():
    """
    Token bucket rate limiter for APIs that regenerate gradually
    (e.g. X tokens per minute).
    """

    def __init__(self, capacity, refill_rate, rate_type='seconds'):
        """
        capacity    = max tokens in the bucket
        refill_rate = tokens regenerated per second
        rate_type = 'seconds', 'minutes', 'hours' or 'day', unit of measure for refill_rate
        """
        
        self.capacity = capacity
        self.tokens = capacity

        self.refill_rate = refill_rate
        self.rate_type = rate_type
        self.last_refill = time.time()
        
        self.locked = False # to avoid using semaphores at this stage, set to True at the request time, set to False when token count is updated after the query is done

        self.lock = threading.Lock()

    def allow_request(self, cost=1):
        """Try to consume tokens. Return True if allowed, else False."""
        with self.lock:
            self.locked = True
            now = time.time()
            elapsed = now - self.last_refill
            # refill based on time passed
            if self.rate_type == 'minutes':
                time_units_elapsed = elapsed % 60
            elif self.rate_type == 'hours':
                time_units_elapsed = elapsed % (60 * 60)
            elif self.rate_type == 'days':
                time_units_elapsed = elapsed % (60 * 60 * 24)
            else:  # default to seconds
                time_units_elapsed = 0
                Warning("rate_type not among considered types")
        
        
            self.tokens = min(self.capacity, self.tokens + time_units_elapsed * self.refill_rate)
            self.last_refill = now

            if self.tokens >= cost:
                return True
            return False
        
    def update_tokens(self, cost=1): #the cost is updated after the query is done    
        with self.lock:
            self.locked = False
            self.tokens -= cost
            
    def AskUpdateCapacity(self):
        # if available asks API how many tokens are available 
        pass

class TokenManager:
    """
    Central dispatcher that manages multiple APIs with different
    rate limiting strategies.
    """
    def __init__(self):
        self.limiters = {
            "Google_AI_Studio": LeakyBucketLimiter(capacity=100, refill_rate=1/60, rate_type='seconds'), #TODO to update, is a placeholder 
            "Claude": LeakyBucketLimiter(capacity=90, refill_rate=90/60, rate_type='seconds'), # to update, is a placeholder
            "OpenAI": LeakyBucketLimiter(capacity=3500, refill_rate=3500/60, rate_type='seconds') # to update, is a placeholder
        }

    def add_api(self, name, limiter):
        """Register an API with its limiter.
            limiter is a LeakyBucketLimiter or similar object
        """
        self.limiters[name] = limiter

    def request(self, name, cost=1):
        """
        Attempt to make a request on a given API.
        Returns True if allowed, False if rate-limited.
        """
        limiter = self.limiters.get(name)
        if limiter is None:
             Warning(f"API '{name}' not registered") #might later change to exception
        return limiter.allow_request(cost)
    
    def __call__(self, cost=1):

        for name, limiter in self.limiters.items():
            if limiter.allow_request(cost):
                return name
        
        
        return None  # All APIs are rate-limited


class LLMQueryManager():
    lock = threading.Lock()  # Class-level lock, trying not to cause probles when using multiple instances

    def __init__(self):
        self.current_index = 0
        
    def get_next_api():
        global current_index

        with LLMQueryManager.lock:            
            
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
            
    def queryGemini(Payload, api_key, model):

        client = genai.Client(api_key= api_key)
        response = client.models.generate_content(
            model = model,
            contents=Payload,
        )
        return response
    
    def format_output(api_name, response):
        '''
        Format the output based on the API response structure.

        '''        
        #TODO: Format
        #TODO: check success code, if unsuccessful, re run the operation and log relevant info 
        pass
    
    def __call__(self, Payload):
     
        api_name, api_url, api_key, model = self.get_next_api()
        
        formatted_payload = self.format_payload(api_name, Payload) #assuming Payload contains all relevant info 
        try:
            if(api_name == "Google_AI_Studio"):
                answer = self.queryGemini(formatted_payload, api_key, model)
            else:
                answer = self.run_api_query(api_url, api_key, model, formatted_payload)
            return self.format_output(answer)
        
        except requests.RequestException as e:
            print(f"API Request failed: {e}")
            return None
    

