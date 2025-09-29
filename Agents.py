import Nodes 
import os
import pandas as pd
from typing import List, Dict
import langchain
from langgraph.graph import Graph, START, END
import numpy as np 

class Agent():
    def __init__(self, name:str):
        self.name = name  
        self.CodeWriter = Nodes.CodeWritingNode()
        self.CodeExecuter = Nodes.CodeExecutionNode()

    def run(self):
        pass

class CodingAgent():
        
    def __init__(self, name:str):
        self.name = name  
        self.CodeWriter = Nodes.CodeWritingNode()
        self.CodeExecuter = Nodes.CodeExecutionNode()

    def run(self):
        pass


class HumanCommunicationAgent():
        def __init__(self, name:str):
            self.name = name  
            self.CodeWriter = Nodes.CodeWritingNode()
            self.CodeExecuter = Nodes.CodeExecutionNode()
    
        def run(self):
            pass


class SocialMediaAgent():
        def __init__(self, name:str):
            self.name = name  
            self.CodeWriter = Nodes.CodeWritingNode()
            self.CodeExecuter = Nodes.CodeExecutionNode()
    
        def run(self):
            pass


class WebSurfer():
        def __init__(self, name:str):
            self.name = name  
            self.CodeWriter = Nodes.CodeWritingNode()
            self.CodeExecuter = Nodes.CodeExecutionNode()
    
        def run(self):
            pass


