import json
from pathlib import Path
from .model import LOCAL_STUDENT_ID,LearningProfile

class LearningProfileStore:
    def __init__(self,path:str|Path="learning_profile_memory.json"):
        self.path=Path(path)

    def load(self):
        if not self.path.exists():
            return LearningProfile(student_id=LOCAL_STUDENT_ID)
        with self.path.open("r",encoding="utf-8") as file:
            profile=LearningProfile.model_validate(json.load(file))
        profile.student_id=LOCAL_STUDENT_ID
        return profile
    
    def save(self,profile:LearningProfile):
        profile.student_id=LOCAL_STUDENT_ID
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("w",encoding="utf-8") as file:
            json.dump(profile.model_dump(mode="json"),file,indent=2)
        return profile
