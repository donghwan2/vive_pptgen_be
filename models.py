from pydantic import BaseModel
from typing import List

# Pydantic 모델
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class PPTRequest(BaseModel):
    report_content: str

class Slide(BaseModel):
    title: str
    svg: str

class PPTResponse(BaseModel):
    slides: List[Slide]
    message: str