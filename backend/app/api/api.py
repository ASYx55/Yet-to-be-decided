from fastapi import FastAPI
from pydantic import BaseModel, Field

application=FastAPI()
student_info={
    "name":"Student",
    "grade":"High School",
    "learning_style":"step by step",
    "strong_points":["integration", "Matrices"],
    "weak_points":["differentiation"],
    }
 
student_memory=[
 {
    "memory_id":"memory01",
    "memory_type":"weakness",
    "subject":"math",
    "topic":"differentiation",
    "detail":"student struggles with continuity problems",
    "confidence":"very low",
 }
]

topic_mastery_score={
    "Integration":95,
    "Matrices":93,
    "Differentiation":40,
}
class StudentInfo(BaseModel):
 name:str
 grade:str
 learning_style:str
 strong_points:list[str]= Field(default_factory=list)
 weak_points:list[str]= Field(default_factory=list)

class StudentInfoUpdate(BaseModel):
 name:str | None = None
 grade:str | None = None
 learning_style:str | None = None
 strong_points:list[str] | None = None
 weak_points:list[str] | None = None

class Memory(BaseModel):
 memory_id: str
 memory_type:str
 subject:str
 topic:str
 detail:str
 confidence:str=Field(default="low")

class ChatReq(BaseModel):
 message:str
 subject:str
 topic:str

class ChatRes(BaseModel):
 reply:str
 concepts_detected:list[str]
 practice_needed:bool

class PracticeGenReq(BaseModel):
 subject:str
 topic:str
 difficulty:str="easy"
 count: int = Field(default=3, ge=1, le=10)

class PracticeGenerate(BaseModel):
 question_id:str
 question:str
 subject:str
 topic:str
 difficulty:str

class PracticeGenRes(BaseModel):
 questions: list[PracticeGenerate]

class PracticeSubReq(BaseModel):
 question_id:str
 answer:str

class PracticeSubRes(BaseModel):
 is_correct:bool
 feedback:str
 mistakes:list[str]
 updated_mastery_score:int

class ProgressRes(BaseModel):
 mastery_scores:dict[str,int]

def get_student_info() -> StudentInfo:
 return StudentInfo(**student_info)

def gen_gemi_rep(prompt:str) -> str:
 return(
  "This is your personalised response"
 )

def check_ans_gemi(ans:str) -> dict:
 lower_ans=ans.lower()
 has_base_case = "if" in lower_ans or "base" in lower_ans
 if has_base_case:
  return{
   "is_correct":True,
   "feedback":"Good Work",
   "mistakes": [],
  }
 return{
 "is_correct":False,
   "feedback":"No base case",
   "mistakes": ["missing base case"],
}

@application.get("/health")
def health_info():
 return{"status": "works", "message": "API is running"}

@application.get("/profile", response_model=StudentInfo)
def read_student_info():
  return get_student_info()

@application.patch("/profile", response_model=StudentInfo) 
def student_info_update(update:StudentInfoUpdate):
 update_data = update.model_dump(exclude_unset=True)
 student_info.update(update_data)
 return StudentInfo(**student_info)

@application.get("/memory", response_model=list[Memory])
def read_student_memory():
 return [Memory(**item) for item in student_memory]

@application.post("/memory", response_model=Memory)
def create_memory(memory: Memory):
 memory_id = f"mem_{len(student_memory) + 1:03d}"

 memory_data = memory.model_dump()
 memory_data["memory_id"] = memory_id
 new_item = memory_data

 student_memory.append(new_item)
 return Memory(**new_item)

@application.post("/chat", response_model=ChatRes)
def chat(request:ChatReq):
 info=get_student_info()

 prompt={
  "student_info":info.model_dump(),
  "student_memory":student_memory,
  "current_question":request.message,
  "subject":request.subject,
  "topic":request.topic,
 }

 reply=gen_gemi_rep(str(prompt))
 practice_needed=request.topic in info.weak_points

 if "not understand" in request.message.lower() or "don't understand" in request.message.lower():
  create_memory(
   Memory(
   memory_id="temp",
   memory_type="weakness",
   subject=request.subject,
   topic=request.topic,
   detail="Student expressed confusion about " + request.topic + ".",
   confidence="low",
   )
  )

 return ChatRes(
  reply=reply,
  concepts_detected=[request.topic],
  practice_needed=practice_needed,
 )

@application.post("/practice/gen", response_model=PracticeGenRes)
def gen_practice(request: PracticeGenReq):
 ques=[]
 for number in range(1,request.count+1):
  ques.append(
   PracticeGenerate(
    question_id="q_{:03d}".format(number),
    question="Practice question " + str(number) + ": Solve problem about " + request.topic + ".",
    subject=request.subject,
    topic=request.topic,
    difficulty=request.difficulty,
   )
  )

 return PracticeGenRes(questions=ques)

@application.post("/practice/submit",response_model=PracticeSubRes)
def submit_practice(request: PracticeSubReq):
 evaluation=check_ans_gemi(request.answer)
 current_score=topic_mastery_score.get("Differentiation",50)

 if evaluation["is_correct"]:
  updated_score=min(current_score+5,100)
 else:
  updated_score=max(current_score-2,0)

 topic_mastery_score["Differentiation"]=updated_score
 return PracticeSubRes(
  is_correct=evaluation["is_correct"],
  feedback=evaluation["feedback"],
  mistakes=evaluation["mistakes"],
  updated_mastery_score=updated_score,
 )

@application.get("/progress", response_model=ProgressRes)
def read_progress():
 return ProgressRes(mastery_scores=topic_mastery_score)



