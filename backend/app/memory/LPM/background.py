import asyncio
import json
from pathlib import Path
from .analyzer import OllamaSignalAnalyzer
from .extractor import LearningProfileExtractor
from .model import ConversationAnalysisRequest,ConversationMessage,ProfileExtraction
from .storage import LOCAL_STUDENT_ID,LearningProfileStore

class ConversationBufferStore:
    def __init__(self,path:str|Path="conversation_buffer_memory.json"):
        self.path=Path(path)

    def append_message(self,subject:str,topic:str,role:str,content:str):
        data=self.read_all()
        previous_topic=data.get("topic")
        data["previous_topic"] = previous_topic if previous_topic and previous_topic !=topic else data.get("previous_topic")
        data["subject"]=subject
        data["topic"]=topic
        data.setdefault("messages",[])
        data.setdefault("processed_count",0)
        data["messages"].append(ConversationMessage(role=role,content=content).model_dump(mode="json"))
        self.write_all(data)

    def append_chat_turn(self,subject:str,topic:str,student_message:str,assistant_reply:str):
        self.append_message(subject,topic,"student",student_message)
        self.append_message(subject,topic,"assistant",assistant_reply)

    def has_pending_messages(self):
        data = self.read_all()
        return len(data.get("messages",[]))>data.get("processed_count",0)
    
    def build_request(self,max_recent_messages:int=8):
        data=self.read_all()
        messages=[ConversationMessage.model_validate(item) for item in data.get("messages",[])]
        processed_count=data.get("processed_count",0)
        if len(messages)<=processed_count:
            return None
        recent_messages=messages[-max_recent_messages:]
        return ConversationAnalysisRequest(student_id=LOCAL_STUDENT_ID,subject=data.get("subject","unknown"),topic=data.get("topic","unknown"),messages=recent_messages,event_type="scheduled_background",previous_topic=data.get("previous_topic"),max_recent_messages=max_recent_messages)
    
    def mark_processed(self):
        data=self.read_all()
        data["processed_count"]=len(data.get("messages",[]))
        self.write_all(data)

    def default_state(self):
        return {"subject":"unknown","topic":"unknown","previous_topic":None,"messages":[],"processed_count":0}
    
    def read_all(self):
        if not self.path.exists():
            return self.default_state()
        with self.path.open("r",encoding="utf-8") as file:
            return json.load(file)
        
    def write_all(self,data:dict):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("w",encoding="utf-8") as file:
            json.dump(data,file,indent=2)

class Layer3BackgroundService:
    def __init__(self,profile_store:LearningProfileStore|None=None,buffer_store: ConversationBufferStore | None = None, analyzer: OllamaSignalAnalyzer | None = None, extractor: LearningProfileExtractor | None = None, interval_seconds: int = 300, max_recent_messages: int = 8):
        self.profile_store=profile_store or LearningProfileStore()
        self.buffer_store=buffer_store or ConversationBufferStore()
        self.analyzer=analyzer or OllamaSignalAnalyzer()
        self.extractor=extractor or LearningProfileExtractor()
        self.interval_seconds=interval_seconds
        self.max_recent_messages=max_recent_messages

    def log_chat_turn(self,subject:str,topic:str,student_message:str,assistant_reply:str):
        self.buffer_store.append_chat_turn(subject,topic,student_message,assistant_reply)

    def log_message(self,subject:str,topic:str,role:str,content:str):
         self.buffer_store.append_message(subject,topic,role,content)

    def process_pending_once(self):
        request=self.buffer_store.build_request(self.max_recent_messages)
        if request is None:
            return None
        profile=self.profile_store.load()
        signals=self.analyzer.analyze(request)
        if not signals:
            return None
        result=self.extractor.extract_from_signals(profile,request,signals)
        self.profile_store.save(result.profile)
        self.buffer_store.mark_processed()
        return result
    
    async def run_forever(self):
        while True:
            self.process_pending_once()
            await asyncio.sleep(self.interval_seconds)