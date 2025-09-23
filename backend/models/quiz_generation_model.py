#quiz_generation_model.py
from pydantic import BaseModel
from typing import Literal, Optional, List, Dict
from fastapi import Form


class QuizRequest(BaseModel):
    youtube_url: Optional[str] = None 
    file: bytes = None
    target_lang: str = "en"
    difficulty: Literal["basic", "medium", "hard"] = Form("medium")
    


class QuizResponse(BaseModel):
    transcript: str
    summary: List[Dict[str, str]]
    quiz: List[Dict]

class VerifyRequest(BaseModel):
    quiz: List[Dict]   # the original quiz returned
    user_answers: Dict[str , int]  # {question_index: chosen_option}
    

class VerifyResponse(BaseModel):
    results: List[Dict[str, str]]  # [{ "question": "...", "your_answer": "...", "correct_answer": "...", "is_correct": True/False }]
    score: float
