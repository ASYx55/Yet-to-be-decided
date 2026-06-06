"""Copyright (c) 2026 Memori74"""
from .model import ConversationAnalysisRequest, EvidenceItem, ExtractedLearningSignal, LearningProfile, MemoryAdapterEntry, ProfileExtraction, SemanticMemoryEvent, StudentInfoUpdateDraft, TopicLearningSignal, utc_now

def normalize_text(value:str):
    return value.lower().replace("’","'").strip()

def clamp(value:float,minimum:float=0.0,maximum:float=1.0):
    return max(minimum,min(maximum,value))

def topic_key(subject:str,topic:str):
    return normalize_text(subject)+"::"+normalize_text(topic)

def confidence_label(score:float):
    if score<0.35:
        return "low"
    if score>0.7:
        return "high"
    return "medium"

def speed_label(score:float):
    if score<0.35:
        return "slow"
    if score>0.7:
        return "fast"
    return "medium"

class LearningProfileExtractor:
    def extract_from_signals(self, profile: LearningProfile, request: ConversationAnalysisRequest, extracted_signals: list[ExtractedLearningSignal]):
        profile.student_id=request.student_id
        grouped_signals=self.group_extracted_signals(extracted_signals)
        memory_updates=[]
        semantic_events=[]
        for grouped_key,topic_signals in grouped_signals.items():
            first_signal=topic_signals[0]
            signal=profile.topics.get(grouped_key)
            if signal is None:
                signal=TopicLearningSignal(subject=first_signal.subject,topic=first_signal.topic)
                profile.topics[grouped_key]=signal
            mistakes=self.collect_signal_mistakes(topic_signals)
            style_signal=self.first_signal_value(topic_signals,"learning_style")
            slow_signal=any(item.speed=="slow"for item in topic_signals)
            fast_signal=any(item.speed=="fast"for item in topic_signals)    
            low_confidence=any(item.signal_type=="confidence" and (item.confidence_label=="low" or item.confidence_score < 0.35) for item in topic_signals)
            high_confidence=any(item.signal_type=="confidence" and (item.confidence_label=="high" or item.confidence_score > 0.7) for item in topic_signals)
            incorrect_detected=any(item.is_correct is False for item in topic_signals)
            correct_detected=any(item.is_correct is True for item in topic_signals)
            weakness_detected = any(item.signal_type in ("weakness", "mistake") for item in topic_signals) or incorrect_detected or bool(mistakes)
            strength_detected=any(item.signal_type=="strength" for item in topic_signals)or(correct_detected and not weakness_detected)
            signal.attempts+=1
            if correct_detected:
                signal.correct_count+=1
            signal.mistake_count+=len(mistakes)
            self.apply_strength_or_weakness(signal,strength_detected,weakness_detected,mistakes)
            self.apply_confidence(signal,low_confidence,high_confidence,correct_detected if correct_detected or incorrect_detected else None)
            self.apply_speed(signal,slow_signal,fast_signal,request.response_time_seconds,correct_detected if correct_detected or incorrect_detected else None)
            self.apply_learning_style(profile,style_signal)
            self.store_extracted_evidence(signal,topic_signals,request)
            memory_updates.extend(self.build_memory_updates(signal,profile,mistakes,strength_detected,weakness_detected,style_signal))
            semantic_events.extend(self.build_semantic_events(signal,profile,strength_detected,weakness_detected))
        self.refresh_profile_rollups(profile)
        profile.updated_at=utc_now()
        student_info_update=StudentInfoUpdateDraft(learning_style=profile.preferred_learning_style,strong_points=profile.strengths,weak_points=profile.weaknesses)
        mastery_score=self.build_mastery_score(profile)
        return ProfileExtraction(profile=profile,student_info_update=student_info_update,extracted_signals=extracted_signals,memory_updates=memory_updates,semantic_memory_events=semantic_events,mastery_scores=mastery_score)
    
    def group_extracted_signals(self,extracted_signals:list[ExtractedLearningSignal]):
        grouped:dict[str,list[ExtractedLearningSignal]]={}
        for signal in extracted_signals:
            key=topic_key(signal.subject,signal.topic)
            grouped.setdefault(key,[]).append(signal)
        return grouped
    
    def collect_signal_mistakes(self,topic_signals:list[ExtractedLearningSignal]):
        mistakes=[]
        for signal in topic_signals:
            mistakes.extend(signal.mistakes)
            if signal.signal_type=="mistake" and signal.detail:
                mistakes.append(signal.detail)
        unique_mistakes=[]
        for mistake in mistakes:
            cleaned=mistake.strip().lower()
            if cleaned and cleaned not in unique_mistakes:
                unique_mistakes.append(cleaned)
        return unique_mistakes
    
    def first_signal_value(self,topic_signals:list[ExtractedLearningSignal],field_name:str):
        for signal in topic_signals:
            value=getattr(signal,field_name)
            if value:
                return value
        return None
    
    def store_extracted_evidence(self,signal:TopicLearningSignal,topic_signals:list[ExtractedLearningSignal],request:ConversationAnalysisRequest):
        evidence_parts=[item.evidence or item.detail for item in topic_signals if item.evidence or item.detail]
        evidence_text="|".join(evidence_parts[:3]) if evidence_parts else "Extracted from recent conversation."
        signal.evidence.append(EvidenceItem(source=request.event_type,text=evidence_text,weight=1.0))
        signal.evidence=signal.evidence[-10:]
        signal.updated_at=utc_now()

    def apply_strength_or_weakness(self,signal:TopicLearningSignal,strength_detected:bool,weakness_detected:bool,mistakes:list[str]):
        if strength_detected:
            signal.strength_score=clamp(signal.strength_score+0.2)
            signal.weakness_score=clamp(signal.weakness_score-0.08)
        if weakness_detected:
            repeated_count=sum(1 for mistake in mistakes if mistake in signal.mistakes)
            signal.weakness_score=clamp(signal.weakness_score+0.2+repeated_count*0.1)
            signal.strength_score=clamp(signal.strength_score-0.05)
        for mistake in mistakes:
            if mistake not in signal.mistakes:
                signal.mistakes.append(mistake)

    def apply_confidence(self,signal:TopicLearningSignal,low_confidence:bool,high_confidence:bool,is_correct:bool|None):
        if low_confidence:
            signal.confidence_score=clamp(signal.confidence_score-0.15)
        if high_confidence:
            signal.confidence_score=clamp(signal.confidence_score+0.1)
        if is_correct is True:
             signal.confidence_score=clamp(signal.confidence_score+0.08)
        if is_correct is False:
            signal.confidence_score=clamp(signal.confidence_score-0.08)

    def apply_speed(self,signal:TopicLearningSignal,slow_signal:bool,fast_signal:bool,response_time_seconds:float|None,is_correct:bool|None):
        if slow_signal:
            signal.speed_score=clamp(signal.speed_score-0.15)
        if fast_signal:
            signal.speed_score=clamp(signal.speed_score+0.1)
        if response_time_seconds is not None and response_time_seconds>90:
            signal.speed_score=clamp(signal.speed_score-0.1)
        if response_time_seconds is not None and response_time_seconds<25 and is_correct is True:
            signal.speed_score=clamp(signal.speed_score+0.1)

    def apply_learning_style(self,profile:LearningProfile,style_signal:str|None):
        if style_signal is None:
            return
        current_score=profile.learning_style_scores.get(style_signal,0.5)
        profile.learning_style_scores[style_signal]=clamp(current_score+0.15)

    def refresh_profile_rollups(self,profile:LearningProfile):
        profile.preferred_learning_style=max(profile.learning_style_scores,key=profile.learning_style_scores.get)
        topic_values=list(profile.topics.values())
        if not topic_values:
            return
        average_confidence=sum(signal.confidence_score for signal in topic_values)/len(topic_values)
        average_speed=sum(signal.speed_score for signal in topic_values)/len(topic_values)
        profile.confidence=confidence_label(average_confidence)
        profile.learning_speed=speed_label(average_speed)
        profile.strengths = sorted({signal.topic for signal in topic_values if self.topic_mastery_score(signal)>=70 and signal.weakness_score<0.45})
        profile.weaknesses = sorted({signal.topic for signal in topic_values if self.topic_mastery_score(signal)<=55 or signal.weakness_score>=0.2})

    def topic_mastery_score(self,signal:TopicLearningSignal):
        correctness_bonus=signal.correct_count/signal.attempts if signal.attempts else 0.0
        raw_score=50+signal.strength_score*25-signal.weakness_score*30+(signal.confidence_score-0.5)*20+correctness_bonus*15
        return int(round(clamp(raw_score,0,100)))
    
    def build_mastery_score(self,profile:LearningProfile):
        return{signal.topic:self.topic_mastery_score(signal) for signal in profile.topics.values()}
    
    def build_memory_updates(self,signal:TopicLearningSignal,profile:LearningProfile,mistakes:list[str],strength_detected:bool,weakness_detected:bool,style_signal:str|None):
        updates=[]
        if weakness_detected:
            detail=f"Student showed weakness in {signal.topic}; mistakes: {', '.join(mistakes) if mistakes else 'model detected weakness'}."
            updates.append(MemoryAdapterEntry(memory_type="weakness",subject=signal.subject,topic=signal.topic,detail=detail,confidence=confidence_label(signal.confidence_score)))
        if strength_detected:
            detail=f"Student showed strength in {signal.topic}."
            updates.append(MemoryAdapterEntry(memory_type="strength",subject=signal.subject,topic=signal.topic,detail=detail,confidence=confidence_label(signal.confidence_score)))
        if style_signal is not None:
            detail=f"Student appears to prefer {style_signal} explanations."
            updates.append(MemoryAdapterEntry(memory_type="learning_style",subject=signal.subject,topic=signal.topic,detail=detail,confidence=profile.confidence))
        return updates
    
    def build_semantic_events(self,signal:TopicLearningSignal,profile:LearningProfile,strength_detected:bool,weakness_detected:bool):
        events=[]
        if weakness_detected:
            text=f"Student struggles with {signal.topic};repeated mistakes include {', '.join(signal.mistakes) if signal.mistakes else 'model detected weakness'}."
            events.append(SemanticMemoryEvent(text=text,topic=signal.topic,memory_type="weakness",importance=0.8,confidence=signal.confidence_score,learning_style=profile.preferred_learning_style,student_id=profile.student_id))
        if strength_detected:
             text=f"Student is showing strength in {signal.topic}."
             events.append(SemanticMemoryEvent(text=text,topic=signal.topic,memory_type="strength",importance=0.6,confidence=signal.confidence_score,learning_style=profile.preferred_learning_style,student_id=profile.student_id))
        return events