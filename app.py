import streamlit as st
import os
import tempfile
import whisper
from deep_translator import GoogleTranslator
import yt_dlp  
import groq  

# Load API key from Streamlit Secrets or Environment Variable
groq_api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
groq_client = groq.Client(api_key=groq_api_key)

# Function to download YouTube video
def download_youtube_video(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': tempfile.gettempdir() + '/youtube_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        audio_path = ydl.prepare_filename(info).replace('.webm', '.wav').replace('.m4a', '.wav')
    return audio_path

# Function to extract audio from uploaded video
def extract_audio(video_path, audio_path="extracted_audio.wav"):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
    return audio_path

# Function to transcribe audio
def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"], result["language"]

# Function to translate transcript
def translate_transcript(text, source_lang, target_lang):
    if source_lang != target_lang:
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    return text  

# Function to generate detailed summary using Groq LLM
def generate_summary_groq(transcript):
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an expert at summarizing transcripts into detailed summaries."},
            {"role": "user", "content": f"Summarize the following transcript in a detailed manner:\n\n{transcript}"}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content if response.choices else "Error generating summary."

# Function to generate quiz questions using Groq LLM
def generate_quiz(transcript, summary, difficulty):
    prompt = f"""
    Based on the following transcript and summary, generate exactly 5 multiple-choice quiz questions with 4 options each.
    The difficulty level should be: {difficulty}.

    TRANSCRIPT:
    {transcript}

    SUMMARY:
    {summary}
    
    IMPORTANT: Follow this format EXACTLY for EACH question. Do not add any other text or introductions.

    Question: [Your question here]
    A) [Option A]
    B) [Option B]
    C) [Option C]
    D) [Option D]
    Answer: [The correct option letter, e.g., B)]
    """

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": "You are an expert quiz generator."},
                  {"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content if response.choices else "Error generating quiz."

# Initialize session state
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = []
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False
if "score" not in st.session_state:
    st.session_state.score = 0

# ---- SIDEBAR ----
st.sidebar.title("🎬 AI Video Processing")

# Option to upload a file or paste a YouTube link
uploaded_file = st.sidebar.file_uploader("📂 Upload a video file", type=["mp4", "avi", "mov", "mkv"])
youtube_url = st.sidebar.text_input("📺 Paste YouTube Video Link")

# User selects output transcript language
language_options = {
    "English": "en", "kannada": "kn","Spanish": "es", "French": "fr", "German": "de",
    "Italian": "it", "Portuguese": "pt", "Russian": "ru", "Hindi": "hi"
}
target_lang = st.sidebar.selectbox("🌍 Select transcript language", list(language_options.keys()))
target_lang_code = language_options[target_lang]

if st.sidebar.button("▶ Process Video"):
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_file.write(uploaded_file.read())
            video_path = temp_file.name
        st.sidebar.info("⏳ Extracting Audio...")
        audio_path = extract_audio(video_path)
    elif youtube_url:
        st.sidebar.info("⏳ Downloading YouTube Audio...")
        audio_path = download_youtube_video(youtube_url)
    else:
        st.sidebar.error("⚠️ Please upload a video file or enter a YouTube link.")
        st.stop()

    st.sidebar.info("⏳ Transcribing Audio...")
    transcript, detected_language = transcribe_audio(audio_path)
    st.session_state.transcript = translate_transcript(transcript, detected_language, target_lang_code)

    st.sidebar.success(f"✅ Detected Language: {detected_language.upper()}")

    st.sidebar.info("⏳ Generating Detailed Summary...")
    st.session_state.summary = generate_summary_groq(st.session_state.transcript)

    # Cleanup temp files
    os.unlink(audio_path)

# ---- MAIN CONTENT ----
st.subheader(" AI Video Summarization & Quiz")

if st.session_state.transcript:
    if uploaded_file:
        st.video(uploaded_file)
    elif youtube_url:
        st.video(youtube_url)

    # Display transcript
    if st.session_state.transcript:
        st.subheader("📜 Final Transcript")
        st.text_area("", st.session_state.transcript, height=200)

    # Display summary
    if st.session_state.summary:
        st.subheader("📌 Detailed Summary")
        st.text_area("", st.session_state.summary, height=200)

    # Quiz Difficulty Selection
    difficulty_level = st.selectbox("🎯 Select Quiz Difficulty", ["Beginner", "Intermediate", "Advanced"])

    if st.button("📝 Take Quiz"):
        with st.spinner("⏳ Generating Quiz..."):
            quiz_text = generate_quiz(st.session_state.transcript, st.session_state.summary, difficulty_level)

        # Initialize lists to hold the structured quiz data
        quiz_questions = []
        quiz_answers = []
        
        # Split the entire quiz text into blocks for each question
        # We assume each question block starts with "Question:"
        question_blocks = quiz_text.strip().split("Question:")[1:]

        for block in question_blocks:
            lines = block.strip().split('\n')
            
            # The first line is always the question text
            question_text = lines[0].strip()
            
            # Find the options and the answer
            options = []
            answer = ""
            for line in lines[1:]: # Check the rest of the lines
                line = line.strip()
                if line.lower().startswith("answer:"):
                    answer = line[len("Answer:"):].strip()
                elif line: # If the line is not empty
                    options.append(line)

            if question_text and options and answer:
                quiz_questions.append({"question": question_text, "options": options})
                quiz_answers.append(answer)

        st.session_state.quiz = quiz_questions
        st.session_state.quiz_answers = quiz_answers
        st.session_state.user_answers = [None] * len(quiz_questions)
        st.session_state.quiz_completed = False
        st.rerun()
    # Display quiz
    # Display quiz only if available
    # Your NEW, BULLETPROOF feedback display
    if st.session_state.quiz:
        st.subheader("🧠 Take the Quiz")

        for i, q in enumerate(st.session_state.quiz):
            st.write(f"**Q{i+1}: {q['question']}**")
            selected_answer = st.radio("Select your answer", q["options"], key=f"q{i}", label_visibility="collapsed")
            st.session_state.user_answers[i] = selected_answer

            # Show feedback below the question after submission
            if st.session_state.quiz_completed:
                user_ans_norm = selected_answer.strip()
                correct_ans_norm = st.session_state.quiz_answers[i].strip()

                # Use the same robust comparison here
                if user_ans_norm and correct_ans_norm and user_ans_norm[0] == correct_ans_norm[0]:
                    st.success(f"✅ Correct! The answer is **{correct_ans_norm}**.")
                else:
                    st.error(f"❌ Incorrect. The correct answer is **{correct_ans_norm}**.")

        # Your NEW, BULLETPROOF scoring logic
        if st.button("✅ Submit Answers"):
            st.session_state.quiz_completed = True
            
            correct_answers_count = 0
            for i in range(len(st.session_state.quiz)):
                # Ensure the strings are not empty before accessing the first character
                user_answer = st.session_state.user_answers[i].strip()
                correct_answer_key = st.session_state.quiz_answers[i].strip()
                
                # This is the new, robust comparison
                if user_answer and correct_answer_key and user_answer[0] == correct_answer_key[0]:
                    correct_answers_count += 1
                    
            st.session_state.score = correct_answers_count
            st.rerun()
                    
            st.session_state.score = correct_answers_count
            st.rerun() # Use rerun to immediately show the feedback

        if st.session_state.quiz_completed:
            st.subheader(f"🏆 Your Final Score: {st.session_state.score} / {len(st.session_state.quiz)}")

