from datetime import datetime,timezone
from pydantic import BaseModel,Field

LOCAL_STUDENT_ID="local_student"

def utc_now():
    return datetime.now(timezone.utc)

def default_learning_style_scores():
    return {"step by step":0.5,"examples":0.5,"visual":0.5,"practice":0.5,"short answer":0.5}

class ConversationMessage(BaseModel):
    role:str
    content:str
    created_at:datetime=Field(default_factory=utc_now)

class ConversationAnalysisRequest(BaseModel):
    student_id:str=LOCAL_STUDENT_ID
    subject:str
    topic:str
    messages:list[ConversationMessage]=Field(default_factory=list)
    event_type:str="scheduled_background"
    previous_topic:str|None=None
    is_correct:bool|None=None
    response_time_seconds:float|None=None
    max_recent_messages:int=8

class ExtractedLearningSignal(BaseModel):
    signal_type:str
    subject:str
    topic:str
    detail:str
    evidence:str=""
    confidence_label:str="medium"
    confidence_score:float=0.5
    mistakes:list[str]=Field(default_factory=list)
    learning_style:str|None=None
    speed:str|None=None
    is_correct:bool|None=None

class EvidenceItem(BaseModel):
    source:str="scheduled_background"
    text:str
    weight:float=1.0
    created_at:datetime=Field(default_factory=utc_now)

class TopicLearningSignal(BaseModel):
    subject:str
    topic:str
    weakness_score:float=0.0
    strength_score:float=0.0
    confidence_score:float=0.5
    speed_score:float=0.5
    attempts:int=0
    correct_count:int=0
    mistake_count:int=0
    mistakes:list[str]=Field(default_factory=list)
    evidence:list[EvidenceItem]=Field(default_factory=list)
    updated_at:datetime=Field(default_factory=utc_now)

class LearningProfile(BaseModel):
    student_id:str=LOCAL_STUDENT_ID
    preferred_learning_style:str="step by step"
    learning_style_scores:dict[str,float]=Field(default_factory=default_learning_style_scores)
    learning_speed:str="medium"
    confidence:str="medium"
    strengths:list[str]=Field(default_factory=list)
    weaknesses:list[str]=Field(default_factory=list)
    topics:dict[str,TopicLearningSignal]=Field(default_factory=dict)
    updated_at:datetime=Field(default_factory=utc_now)

class StudentInfoUpdateDraft(BaseModel):
    learning_style:str|None=None
    strong_points:list[str]|None=None
    weak_points:list[str]|None=None

class MemoryAdapterEntry(BaseModel):
    memory_id:str="layer3_pending"
    memory_type:str
    subject:str
    topic:str
    detail:str
    confidence:str="medium"

class SemanticMemoryEvent(BaseModel):
    text:str
    topic:str
    memory_type:str
    importance:float=0.5
    confidence:float=0.5
    learning_style:str|None=None
    student_id:str=LOCAL_STUDENT_ID

class ProfileExtraction(BaseModel):
    profile:LearningProfile
    student_info_update:StudentInfoUpdateDraft
    extracted_signals:list[ExtractedLearningSignal]=Field(default_factory=list)
    memory_updates:list[MemoryAdapterEntry]=Field(default_factory=list)
    semantic_memory_events:list[SemanticMemoryEvent]=Field(default_factory=list)
    mastery_scores:dict[str,int]=Field(default_factory=dict)


