from queryComp import queryGemini

import numpy as np
import pandas as pd 
import os 
from kaggle.api.kaggle_api_extended import KaggleApi
from typing import List, Dict
import json
from io import StringIO




class ManagerNode:
    def __init__(self, name="ManagerNode"):
        self.name = name

    def run(self, task_description: str, available_tools: List[str]) -> Dict[str, str]:
        # Placeholder logic for task decomposition
        subtasks = [{"subtask": f"Subtask {i+1} for {task_description}"} for i in range(3)]
        return {"task_description": task_description, "subtasks": subtasks}

    def __call__(self, task_description: str, available_tools: List[str]) -> Dict[str, str]:
        return self.run(task_description, available_tools)



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

class CodeWriterNode:

    def __init__(self):
        pass

    def __call__(self):
        pass


class CodeCheckingNode:
    def __init__(self):
        pass


class WebSearchNode:
    def __init__(self):
        pass

class TelegramNode:
    def __init__(self):
        pass


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
