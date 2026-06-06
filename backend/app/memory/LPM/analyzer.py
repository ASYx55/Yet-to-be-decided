"""Copyright (c) 2026 Memori74"""
import json
from urllib import request as url_request
from urllib.error import URLError,HTTPError
from .model import ConversationAnalysisRequest,ExtractedLearningSignal

def normalize(value:str):
    """Normalizes text for fallback matching."""
    return value.lower().replace("’", "'").strip()

def has_any(text:str,phrases:tuple[str,...]):
    """Checks whether text contains any phrase."""
    normalized=normalize(text)
    for phrase in phrases:
        if phrase in normalized:
            return True
    return False

class OllamaSignalAnalyzer:
    """Extracts learning signals using a free local Ollama model."""
    def __init__(self,model_name: str ="qwen3:4b",
                 ollama_url:str ="http://localhost:11434/api/generate",
                 timeout_seconds:int=60,
                 use_fallback:bool=True):
        self.model_name=model_name
        self.ollama_url=ollama_url
        self.timeout_seconds=timeout_seconds
        self.use_fallback=use_fallback

    def analyze(self,request:ConversationAnalysisRequest):
        """Extracts learning signals from raw recent chat."""
        prompt=self.build_prompt(request)
        response_text=self.call_ollama(prompt)
        signals=self.parse_model_response(response_text,request)if response_text else []
        if signals:
            return signals
        if self.use_fallback:
            return self.local_fallback(request)
        return[]

    def call_ollama(self,prompt:str):
        """Calls Ollama's local HTTP API."""
        payload={"model":self.model_name,
                "prompt":prompt,
                "stream":False,
                "format":"json",
                "options":{"temperature":0.1}}
        body=json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        http_request=url_request.Request(self.ollama_url,data=body,headers=headers,method="POST")
        try:
            with url_request.urlopen(http_request,timeout=self.timeout_seconds) as response:
                data=json.loads(response.read().decode("utf-8"))
                return data.get("response","")
        except(URLError,HTTPError,TimeoutError,json.JSONDecodeError):
            return ""

    def build_prompt(self,request: ConversationAnalysisRequest):
        """Builds the structured extraction prompt for the local model."""
        recent_messages=request.messages[-request.max_recent_messages:]
        transcript_lines=[]
        for message in recent_messages:
            transcript_lines.append(f"{message.role}: {message.content}")
        transcript="\n".join(transcript_lines)
        return f"""
            You are Layer 3 Learning Profile Memory for a STEM tutoring app.
            Your job is to extract learning signals from the raw transcript.
            Do not answer the student.
            Return JSON only.
            Only extract signals supported by transcript evidence.
            Valid signal_type values: weakness, strength, mistake, confidence, speed, learning_style, neutral.
            Use this exact JSON shape:
            {{"signals":[{{"signal_type":"weakness",
            "subject":"{request.subject}",
            "topic":"{request.topic}",
            "detail":"short extracted detail",
            "evidence":"short evidence from transcript",
            "confidence_label":"low",
            "confidence_score":0.8,
            "mistakes":["optional mistake"],
            "learning_style":null,
            "speed":null,
            "is_correct":false}}]}}
            Subject:{request.subject}
            Topic:{request.topic}
            Event Type:{request.event_type}
            Known correctness if provided:{request.is_correct}
            Transcript:{transcript}"""

    def parse_model_response(self,response_text:str,request:ConversationAnalysisRequest):
        """Parses model JSON into typed signals."""
        json_text=self.extract_json_object(response_text)
        if not json_text:
            return []
        try:
            data=json.loads(json_text)
        except json.JSONDecodeError:
            return[]
        raw_signals=data.get("signals",[]) if isinstance(data,dict) else[]
        signals=[]
        for raw_signal in raw_signals:
            if not isinstance(raw_signal, dict):
                continue
            raw_signal.setdefault("subject",request.subject)
            raw_signal.setdefault("topic",request.topic)
            try:
                signals.append(ExtractedLearningSignal.model_validate(raw_signal))
            except Exception:
                continue
        return signals

    def extract_json_object(self,response_text:str):
        """Extracts the first JSON object from model text."""
        text=response_text.strip()
        if text.startswith("```"):
            text=text.replace("```json","").replace("```","").strip()
        start=text.find("{")
        end=text.rfind("}")
        if start==-1 or end ==-1 or end<=start:
            return ""
        return text[start:end+1]

    def local_fallback(self,request:ConversationAnalysisRequest):
        """Extracts obvious signals without a model for local tests."""
        recent_messages=request.messages[-request.max_recent_messages:]
        transcript = "\n".join(message.role + ": " + message.content for message in recent_messages)
        normalized=normalize(transcript)
        signals=[]
        if request.is_correct is False or has_any(normalized,("incorrect",
                                                        w"wrong",
                                                        "not correct",
                                                        "forgot",
                                                        "mistake",
                                                        "error")):
            mistakes=self.infer_mistakes(normalized)
            detail="Student made an error in" + request.topic
            signals.append(ExtractedLearningSignal(signal_type="weakness",
                            subject=request.subject,
                            topic=request.topic,detail=detail,
                            evidence=self.short_evidence(transcript),
                            confidence_label="high",
                            confidence_score=0.8,
                            mistakes=mistakes,
                            is_correct=False))
        if request.is_correct is True or (has_any(normalized,
                                        ("good work",
                                        "well done",
                                        "that is right"))
                                        or ("correct" in normalized and "not correct" 
                                        not in normalized and "incorrect" not in normalized)):
            detail = "Student showed correct understanding in " + request.topic
            signals.append(ExtractedLearningSignal(signal_type="strength",
                            subject=request.subject,
                            topic=request.topic,
                            detail=detail,
                            evidence=self.short_evidence(transcript),
                            confidence_label="medium",
                            confidence_score=0.65,
                            is_correct=True))
        if has_any(normalized, ("don't understand", 
                                "dont understand", 
                                "confused", 
                                "stuck", 
                                "lost", 
                                "not sure")):
            detail = "Student showed low confidence or confusion in " + request.topic
            signals.append(ExtractedLearningSignal(signal_type="confidence",
                            subject=request.subject,
                            topic=request.topic,
                            detail=detail,
                            evidence=self.short_evidence(transcript),
                            confidence_label="low",
                            confidence_score=0.25))
        style = self.infer_learning_style(normalized)
        if style is not None:
            detail = "Student appears to prefer " + style + " explanations"
            signals.append(ExtractedLearningSignal(signal_type="learning_style",
                            subject=request.subject,
                            topic=request.topic,
                            detail=detail,
                            evidence=self.short_evidence(transcript),
                            confidence_label="medium",
                            confidence_score=0.6,
                            learning_style=style))
        if request.response_time_seconds is not None and request.response_time_seconds > 90:
            detail = "Student took a long time on " + request.topic
            signals.append(ExtractedLearningSignal(signal_type="speed",
                            subject=request.subject,
                            topic=request.topic,
                            detail=detail,
                            evidence="response_time_seconds=" + str(request.response_time_seconds),
                            confidence_label="medium",
                            confidence_score=0.6,
                            speed="slow"))
        if not signals:
            signals.append(ExtractedLearningSignal(signal_type="neutral",
                            subject=request.subject,
                            topic=request.topic,
                            detail="No strong learning signal found.",
                            evidence=self.short_evidence(transcript),
                            confidence_label="low",
                            confidence_score=0.2))
        return signals

    def infer_mistakes(self):
        return ["unspecified mistake"]

    def infer_learning_style(self,normalized:str):
        """ Infers learning style from transcript language."""
        if has_any(normalized, ("step by step","break it down","slowly","from basics")):
            return "step by step"
        if has_any(normalized, ("diagram","graph","visual","draw")):
            return "visual"
        if has_any(normalized, ("example","sample","show me")):
            return "examples"
        if has_any(normalized, ("practice","quiz","exercise","test me")):
            return "practice"
        if has_any(normalized, ("short","brief","summary","concise")):
            return "short answer"
        return None

    def short_evidence(self,transcript:str):
        compact=" ".join(transcript.split())
        return compact[:220]












