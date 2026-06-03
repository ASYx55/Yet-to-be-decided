import asyncio
import json
from pathlib import Path
from .analyze import OllamaSignalAnalyzer
from .extractor import LearningProfileExtractor
from .model import ConversationAnalysisRequest,ConversationMessage,ProfileExtraction
from .storage import LearningProfileStore

class ConversationBufferStore:
    def __init__(self,path:str|Path="conversation_buffer_memory.json"):
        self.path=Path(path)

    def append_message(self,subject:str,topic:str,role:str,content:str):
        data=self.read_all()
        
