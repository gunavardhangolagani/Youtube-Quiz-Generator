#quiz_generation_controller.py
import tempfile
from deep_translator import GoogleTranslator
import yt_dlp  

from utils.processing import fn_generate_quiz
from utils.processing import fn_generate_summary
from utils.processing import fn_transcribe_audio
from utils.processing import fn_extract_audio

import os
import json

def fn_download_youtube_video(youtube_url):
    """
    Downloads the audio from a YouTube URL and saves it as a WAV file.
    Returns path to WAV file or raises a RuntimeError with a clean message.
    """
    temp_dir = tempfile.gettempdir()
    outtmpl = temp_dir + '/youtube_audio.%(ext)s'
    cookies_path = "/etc/secrets/YTDLP_COOKIES"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'quiet': True,
    }
    if os.path.exists(cookies_path):
        ydl_opts['cookies'] = cookies_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            generated = ydl.prepare_filename(info)

            # Replace with .wav (post-processor output)
            if '.' in generated:
                audio_path = generated.rsplit('.', 1)[0] + '.wav'
            else:
                audio_path = generated + '.wav'

        return audio_path
    except yt_dlp.utils.DownloadError as e:
        raise RuntimeError(f"Failed to download video: {str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error while processing YouTube URL: {str(e)}") from e



def help_fn_extract_audio(video_path):
    """
    Extracts audio from a video file and saves as a WAV in the system temp dir.
    Returns the path to the audio file.
    """
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_audio_path = temp_audio.name
    temp_audio.close()
    return fn_extract_audio(video_path, temp_audio_path)


def help_fn_transcribe_audio(audio_path):
    """
    Transcribes audio using OpenAI's Whisper model.

    Args:
        audio_path: The file path to the audio file.

    Returns:
        A tuple containing the transcript text and the detected language.
    """
    return fn_transcribe_audio(audio_path)


def fn_translate_transcript(text, source_lang, target_lang):
    """
    Translates text from a source language to a target language.

    Args:
        text: The text to translate.
        source_lang: The source language code (e.g., 'en').
        target_lang: The target language code (e.g., 'es').

    Returns:
        The translated text. Returns original text if source and target are the same.
    """
    if source_lang != target_lang:
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    return text  

def help_fn_generate_summary_groq(transcript):
    var_prompt = f"""
    Based on the following transcript generate summary in bullet points.
    TRANSCRIPT:
    {transcript}
    The output response should be in the following JSON array format Do not give anything extra additional information.
    [
        {{
            "Summary": "summary_text"
        }}
    ]
    """
    return fn_generate_summary(var_prompt)

def help_fn_generate_quiz(transcript, summary, difficulty):
    """
    This helper function is used to generate a quiz using Groq API
    """
    var_prompt = f"""
    Based on the following transcript and summary, generate exactly 5 multiple-choice quiz questions with 4 options each.
    The difficulty level should be: {difficulty}.

    TRANSCRIPT:
    {transcript}

    SUMMARY:
    {summary}

    Output must be a valid JSON array, strictly like this format Do not give anything extra additional information.
    [
        {{
            "question": "What is ...?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correctAnswer": 1,  // 0-based index of the correct option
            "explanation": "Why this answer is correct."
        }}
    ]    """
    response = fn_generate_quiz(var_prompt)

    if isinstance(response, str):
        var_response = json.loads(response)
    else:
        var_response = response

    return var_response





















# def fn_parse_quiz(quiz_text):
#     questions = []
#     question_blocks = [block.strip() for block in quiz_text.split("Question:") if block.strip()]

#     for block in question_blocks:
#         lines = [line.strip() for line in block.splitlines() if line.strip()]

#         match lines:
#             case [question, opt_a, opt_b, opt_c, opt_d, answer_line] if answer_line.startswith("Answer:"):
#                 answer = answer_line.removeprefix("Answer:").strip()
#                 questions.append({
#                     "question": question,
#                     "options": {
#                         "A": opt_a.removeprefix("A)").strip(),
#                         "B": opt_b.removeprefix("B)").strip(),
#                         "C": opt_c.removeprefix("C)").strip(),
#                         "D": opt_d.removeprefix("D)").strip(),
#                     },
#                     "answer": answer
#                 })

#             case _:
#                 print(f"Skipping malformed or non-standard quiz block: {block}")

#     return questions
