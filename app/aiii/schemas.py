from pydantic import BaseModel

class AIRequest(BaseModel):

    question: str



class AIResponse(BaseModel):

    question: str

    answer: str