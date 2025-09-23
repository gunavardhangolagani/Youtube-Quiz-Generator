#quiz_generation_route.py
from fastapi import APIRouter, File, UploadFile, Form
from typing import Literal
from controllers.quiz_generation_controller import (
    fn_download_youtube_video,
    help_fn_extract_audio,
    help_fn_transcribe_audio,
    fn_translate_transcript,
    help_fn_generate_quiz,
    help_fn_generate_summary_groq,
    # fn_parse_quiz
)
from utils.processing import fn_verify_answers
from models.quiz_generation_model import VerifyRequest

from models.quiz_generation_model import QuizResponse
import tempfile
import os
router = APIRouter()

@router.post("/upload_file/", response_model=QuizResponse)
async def fn_upload_file_(
    file: UploadFile = File(...),
    target_lang: str = Form("en"),
    difficulty: Literal["basic", "medium", "hard"] = Form("medium")
):
    video_path, audio_path = None, None

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(await file.read())
        video_path = temp_video.name

    audio_path = help_fn_extract_audio(video_path)
    transcript, detected_lang = help_fn_transcribe_audio(audio_path)
    final_transcript = fn_translate_transcript(transcript, detected_lang, target_lang)
    summary = help_fn_generate_summary_groq(final_transcript)
    quiz = help_fn_generate_quiz(final_transcript, summary, difficulty)

    if video_path and os.path.exists(video_path):
        os.unlink(video_path)
    if audio_path and os.path.exists(audio_path):
        os.unlink(audio_path)

    return QuizResponse(
        transcript=final_transcript,
        summary=summary,
        quiz=quiz
    )
            
            
            
@router.post("/youtube_link/", response_model=QuizResponse)
async def fn_youtube_link(youtube_url: str = Form(...), target_lang: str = Form("en"), difficulty: Literal["basic", "medium", "hard"] = Form("medium")):
    audio_path = fn_download_youtube_video(youtube_url)
    transcript, detected_lang = help_fn_transcribe_audio(audio_path)
    final_transcript = fn_translate_transcript(transcript, detected_lang, target_lang)
    summary = help_fn_generate_summary_groq(final_transcript)
    quiz = help_fn_generate_quiz(final_transcript, summary, difficulty)

    if audio_path and os.path.exists(audio_path):
        os.unlink(audio_path)

    return QuizResponse(
        transcript=final_transcript,
        summary=summary,
        quiz=quiz
    )

@router.post("/verify_answers")
async def verify_user_answers(request: VerifyRequest):
    """
    Verifies the user's answers against the original quiz.
    Ensures the response matches frontend expectations.
    """
    quiz = request.quiz
    user_answers = request.user_answers or {}

    # Convert keys to integers safely (frontend might send string keys)
    user_answers_int = {}
    for k, v in user_answers.items():
        try:
            user_answers_int[int(k)] = v
        except ValueError:
            continue  # skip invalid keys

    # Use your existing utility function
    results = fn_verify_answers(quiz, user_answers_int)

    # Ensure details array is always present and complete
    if "details" not in results or not isinstance(results["details"], list):
        results["details"] = []

    # Optional: Fill in missing explanations or answers if backend data is incomplete
    for idx, detail in enumerate(results["details"]):
        detail.setdefault("question", quiz[idx].get("question", f"Question {idx + 1}"))
        detail.setdefault("userAnswer", None)
        detail.setdefault("correctAnswer", quiz[idx]["options"][quiz[idx]["correctAnswer"]])
        detail.setdefault("explanation", quiz[idx].get("explanation", "No explanation provided."))
        detail.setdefault("isCorrect", False)

    return results
    