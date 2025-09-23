import streamlit as st
import os
import tempfile
from quiz_generation_controller import (
    extract_audio, fn_download_youtube_video, transcribe_audio,
    translate_transcript, generate_summary_groq, generate_quiz, fn_parse_quiz
)

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

uploaded_file = st.sidebar.file_uploader("📂 Upload a video file", type=["mp4", "avi", "mov", "mkv"])
youtube_url = st.sidebar.text_input("📺 Paste YouTube Video Link")

language_options = {
    "English": "en", "Kannada": "kn", "Spanish": "es", "French": "fr",
    "German": "de", "Italian": "it", "Portuguese": "pt", "Russian": "ru", "Hindi": "hi"
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
        audio_path = fn_download_youtube_video(youtube_url)
    else:
        st.sidebar.error("⚠️ Please upload a video file or enter a YouTube link.")
        st.stop()

    st.sidebar.info("⏳ Transcribing Audio...")
    transcript, detected_language = transcribe_audio(audio_path)
    st.session_state.transcript = translate_transcript(transcript, detected_language, target_lang_code)

    st.sidebar.success(f"✅ Detected Language: {detected_language.upper()}")
    st.sidebar.info("⏳ Generating Detailed Summary...")
    st.session_state.summary = generate_summary_groq(st.session_state.transcript)
    os.unlink(audio_path)

# ---- MAIN CONTENT ----
st.subheader(" AI Video Summarization & Quiz")

if st.session_state.transcript:
    if uploaded_file:
        st.video(uploaded_file)
    elif youtube_url:
        st.video(youtube_url)

    st.subheader("📜 Final Transcript")
    st.text_area("", st.session_state.transcript, height=200)

    if st.session_state.summary:
        st.subheader("📌 Detailed Summary")
        st.text_area("", st.session_state.summary, height=200)

    difficulty_level = st.selectbox("🎯 Select Quiz Difficulty", ["Beginner", "Intermediate", "Advanced"])

    if st.button("📝 Take Quiz"):
        with st.spinner("⏳ Generating Quiz..."):
            quiz_text = generate_quiz(st.session_state.transcript, st.session_state.summary, difficulty_level)

        quiz_data = fn_parse_quiz(quiz_text)
        st.session_state.quiz = [ {"question": q["question"], "options": list(q["options"].values())} for q in quiz_data ]
        st.session_state.quiz_answers = [q["answer"] for q in quiz_data]
        st.session_state.user_answers = [None] * len(quiz_data)
        st.session_state.quiz_completed = False
        st.rerun()

    if st.session_state.quiz:
        st.subheader("🧠 Take the Quiz")
        for i, q in enumerate(st.session_state.quiz):
            st.write(f"**Q{i+1}: {q['question']}**")
            selected_answer = st.radio("Select your answer", q["options"], key=f"q{i}", label_visibility="collapsed")
            st.session_state.user_answers[i] = selected_answer
            if st.session_state.quiz_completed:
                if selected_answer and selected_answer[0] == st.session_state.quiz_answers[i][0]:
                    st.success(f"✅ Correct! The answer is **{st.session_state.quiz_answers[i]}**.")
                else:
                    st.error(f"❌ Incorrect. The correct answer is **{st.session_state.quiz_answers[i]}**.")

        if st.button("✅ Submit Answers"):
            st.session_state.quiz_completed = True
            st.session_state.score = sum(
                1 for i in range(len(st.session_state.quiz))
                if st.session_state.user_answers[i] and st.session_state.user_answers[i][0] == st.session_state.quiz_answers[i][0]
            )
            st.rerun()

        if st.session_state.quiz_completed:
            st.subheader(f"🏆 Your Final Score: {st.session_state.score} / {len(st.session_state.quiz)}")
