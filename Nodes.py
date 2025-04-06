from queryComp import queryGemini
import numpy as np
import pandas as pd 
import os 
from APIKeys import Kaggle_API
from kaggle.api.kaggle_api_extended import KaggleApi
from typing import List, Dict
import json
from io import StringIO



# Generic LLM 
class LLMNode:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, prompt: str) -> str:
        return self.run(prompt)

# Code execution
class CodeExecutionNode:
    def __init__(self, name="CodeExecutionNode"):
        self.name = name

    def run(self, code: str) -> dict:
        local_context = {}
        try:
            exec(code, {}, local_context)
            result = {k: v for k, v in local_context.items() if not k.startswith("_")}
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def __call__(self, code: str) -> dict:
        return self.run(code)

# Kaggle Data Import

class KaggleImport:
    def __init__(self, name: str):
        self.name = name
        self.api = KaggleApi()

    def authenticate(self):
        self.api.authenticate()
      
    def load_csv_as_pd(self, identifier: str) -> pd.DataFrame:
        self.api.dataset_download_files(identifier, path='datasets/kaggle', unzip=True)
        extracted_files = os.listdir('datasets/kaggle')
        csv_files = [file for file in extracted_files if file.endswith('.csv')]
        
        if not csv_files:
            raise FileNotFoundError("No CSV file found.")
        
        file_name = f'datasets/kaggle/{csv_files[0]}'  #TODO gestione file multipli
        df = pd.read_csv(file_name)
        
        # Clean up the file after reading
        os.remove(file_name)
        
        return df

    def run(self, dataType: str, identifier: str) -> np.ndarray:
        self.authenticate()
        if dataType == 'csv':
            return self.load_csv_as_pd(identifier)
        else:
            raise ValueError("Unsupported data type. Use 'csv'.")

    def __call__(self, dataType: str, identifier: str) -> np.ndarray:
        return self.run(dataType, identifier)

# Schema Picker 
