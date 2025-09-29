import os
from dotenv import load_dotenv

load_dotenv()  

API_List = {
    "Google_AI_Studio": {
        "URL": f"{os.getenv('GOOGLE_AI_STUDIO_URL')}?key={os.getenv('GOOGLE_AI_STUDIO_KEY')}", #I am kinda lazy at this point
        "Key": os.getenv("GOOGLE_AI_STUDIO_KEY"),
        "Model": "gemini-2.0-flash"
    },
    "OpenAI": {
        "URL": os.getenv("OPENAI_URL"),
        "Key": os.getenv("OPENAI_KEY"),
        "Model": os.getenv("OPENAI_MODEL")
    },
    "OpenAI": {
        "URL": os.getenv("OPENAI_URL"),
        "Key": os.getenv("OPENAI_KEY"),
        "Model": os.getenv("OPENAI_MODEL")
    },
    "OpenAI": {
        "URL": os.getenv("OPENAI_URL"),
        "Key": os.getenv("OPENAI_KEY"),
        "Model": os.getenv("OPENAI_MODEL")
    },
    "OpenAI": {
        "URL": os.getenv("OPENAI_URL"),
        "Key": os.getenv("OPENAI_KEY"),
        "Model": os.getenv("OPENAI_MODEL")
    },

}

LLM_by_type = {
    "text": ["Google_AI_Studio", "OpenAI", "Claude"],
    "code": ["OpenAI", "Google_AI_Studio"],
    "image": ["DALL-E", "Google_AI_Studio"],
    "generic": ["Google_AI_Studio", "OpenAI", "Claude"],
    }