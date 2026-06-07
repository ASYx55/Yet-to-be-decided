"""Copyright (c) 2026 Memori74"""
from .analyzer import OllamaSignalAnalyzer
from .extractor import LearningProfileExtractor
from .model import ConversationAnalysisRequest, ConversationMessage, LOCAL_STUDENT_ID
from .storage import LearningProfileStore

class Layer3MessageProcessor:
    """Processes new chat turns when the API receives them."""
    def __init__(self,profile_store:LearningProfileStore|None=None,
                analyzer:OllamaSignalAnalyzer|None=None,
                extractor:LearningProfileExtractor|None=None,
                max_recent_messages:int=8):
        self.profile_store=profile_store or LearningProfileStore()
        self.analyzer=analyzer or OllamaSignalAnalyzer()
        self.extractor=extractor or LearningProfileExtractor()
        self.max_recent_messages=max_recent_messages

    def process_chat_turn(self,subject:str,topic:str,student_message:str,assistant_reply:str):
        """Processes one completed student+assistant turn."""
        messages=[ConversationMessage(role="student",
                                    content=student_message),
                                    ConversationMessage(role="assistant",content=assistant_reply)]
        request=ConversationAnalysisRequest(student_id=LOCAL_STUDENT_ID,
                                        subject=subject,
                                        topic=topic,
                                        messages=messages[-self.max_recent_messages :],
                                        event_type="chat_turn",
                                        max_recent_messages=self.max_recent_messages)
        signals=self.analyzer.analyze(request)
        if not signals:
            return None
        profile=self.profile_store.load()
        result=self.extractor.extract_from_signals(profile,request,signals)
        self.profile_store.save(result.profile)
        return result

Layer3BackgroundService = Layer3MessageProcessor
