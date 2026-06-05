from pathlib import Path
from tempfile import TemporaryDirectory
from .background import ConversationBufferStore,Layer3BackgroundService
from .model import ConversationAnalysisRequest,ExtractedLearningSignal
from .storage import LearningProfileStore

class FakeAnalyzer:
    def analyze(self,request:ConversationAnalysisRequest):
        return [ExtractedLearningSignal(signal_type="weakness",subject=request.subject,topic=request.topic,detail="Student forgot the inner derivative.",evidence="Assistant said the chain rule was missing.",confidence_label="high",confidence_score=0.8,mistakes=["forgot inner derivative"],is_correct=False),ExtractedLearningSignal(signal_type="learning_style",subject=request.subject,topic=request.topic,detail="Student asked for step-by-step help.",evidence="Student asked to break it down step by step.",confidence_label="medium",confidence_score=0.6,learning_style="step by step")]
    
def run_demo():
    with TemporaryDirectory() as folder:
        root=Path(folder)
        profile_store=LearningProfileStore(root/"profile.json")
        buffer_store=ConversationBufferStore(root/"buffer.json")
        service=Layer3BackgroundService(profile_store=profile_store,buffer_store=buffer_store,analyzer=FakeAnalyzer())
        service.log_chat_turn("math","differentiation","I think derivative of sin(x^2) is cos(x^2).","That is not correct because the chain rule is missing.")
        service.log_chat_turn("math","differentiation","Can you break it down step by step?","Sure, first identify the inside function.")
        result=service.process_pending_once()
        assert result is not None
        assert "differentiation" in result.profile.weaknesses
        assert result.profile.preferred_learning_style=="step by step"
        print(result.model_dump_json(indent=2))

if __name__=="__main__":
    run_demo()
