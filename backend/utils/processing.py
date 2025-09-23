#utills.py

import groq  
from dotenv import load_dotenv
import os
import whisper
import subprocess
import json
import re

load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')
groq_client = groq.Client(api_key=groq_api_key)

def fn_generate_quiz(prompt):
    """
    Calls Groq API and returns JSON-parsed quiz if possible.
    """
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful AI that generates quiz from the given transcript."},
            {"role": "user", "content": prompt}
        ],    
    )
    
    if not response.choices:
        return []

    raw_text = response.choices[0].message.content.strip()

    # Remove optional markdown fences (```json ... ```)
    raw_text = re.sub(r"^```json|```$", "", raw_text, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw_text)   # return parsed JSON directly
    except json.JSONDecodeError:
        print("Could not parse model output as JSON:\n", raw_text)
        return []

# The below function is created , if we want to use two different models for summary and quiz generation.

def fn_generate_summary(prompt):
    """
    This function generates summary using the Groq API.

    Args:
        prompt (str): The prompt to generate text for.
        role (str, optional): The role of the user. Defaults to "user".

    Returns:
        str: The generated text.
    """
    
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
          messages=[
            {"role": "system", "content": "You are a helpful AI that summarizes transcripts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    if not response.choices:
        return []

    raw_text = response.choices[0].message.content.strip()

    # Remove optional markdown fences (```json ... ```)
    raw_text = re.sub(r"^```json|```$", "", raw_text, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw_text)   # ✅ return parsed JSON directly
    except json.JSONDecodeError:
        print("⚠️ Could not parse model output as JSON:\n", raw_text)
        return []   

# The below Fn is created because in future we might use other models like assembly ai.
def fn_transcribe_audio(audio):
    """
    This function transcribes audio from the given audio file.

    Args:
        audio (str): The audio to transcribe.
    """
    model = whisper.load_model("base")
    result = model.transcribe(audio)
    return result["text"], result["language"]


def fn_extract_audio(video_path, audio):
    """
    Extracts audio from a video file using FFmpeg and saves it as a WAV file.

    Args:
        video_path (str): The file path to the video.
        audio_path (str): The file path to save the extracted audio (default: extracted_audio.wav).

    Returns:
        str: The file path to the extracted WAV audio file.
    """
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vn",  # Skip video
        "-acodec", "pcm_s16le",  # WAV format
        "-ar", "44100",  # Sampling rate
        "-ac", "2",      # Stereo
        audio,
        "-y"  # Overwrite if the file already exists
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return audio

# utils/processing.py

def fn_verify_answers(quiz, user_answers):
    """
    Verifies user answers against the quiz.

    Args:
        quiz (List[Dict]): Original quiz questions.
        user_answers (Dict[int, str]): {question_index: chosen_option}

    Returns:
        Dict: Results in frontend-ready format with 'details', 'score', 'total', 'percentage'
    """
    results = []
    correct_count = 0

    for i, q in enumerate(quiz):
        # Get user's answer, fallback to None if missing
        user_ans_idx = user_answers.get(i)
        correct_ans_idx = q.get("correctAnswer", 0)

        # Determine if correct
        is_correct = user_ans_idx == correct_ans_idx
        if is_correct:
            correct_count += 1

        # Build a frontend-ready detail object
        results.append({
            "question": q.get("question", f"Question {i + 1}"),
            "userAnswer": q["options"][user_ans_idx] if user_ans_idx is not None else None,
            "correctAnswer": q["options"][correct_ans_idx],
            "isCorrect": is_correct,
            "explanation": q.get("explanation", "No explanation provided.")
        })

    total_questions = len(quiz)
    percentage = round((correct_count / total_questions) * 100) if total_questions > 0 else 0

    return {
        "details": results,
        "score": correct_count,
        "total": total_questions,
        "percentage": percentage
    }
