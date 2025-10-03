import streamlit as st
from dotenv import load_dotenv
import os
import groq
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
groq_client = groq.Client(api_key=groq_api_key)

# Prompt template
SUMMARY_PROMPT = """
You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing the important points in
bullet form within 250 words. Please provide the summary of the text given here:
"""

# Function: Extract transcript details from YouTube
def extract_transcript_details(youtube_video_url: str) -> str:
    try:
        # Extract video ID
        if "v=" in youtube_video_url:
            video_id = youtube_video_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[1].split("?")[0]
        else:
            raise ValueError("Invalid YouTube URL format")

        # Initialize API instance
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id)  # iterable transcript

        transcript = " ".join(snippet.text for snippet in fetched_transcript)
        return transcript

    except Exception as e:
        st.error(f"Error fetching transcript: {str(e)}")
        return ""

# Function: Generate summary using Groq API
def fn_generate_summary(transcript_text: str, base_prompt: str) -> str:
    """
    Generates a summary using the Groq API.
    """
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": transcript_text},
        ],
        temperature=0.7,
    )

    if not response.choices:
        return "No summary generated."

    return response.choices[0].message.content.strip()

# Streamlit App UI
st.title("🎥 YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    # Extract and show thumbnail
    if "v=" in youtube_link:
        video_id = youtube_link.split("v=")[1].split("&")[0]
    elif "youtu.be/" in youtube_link:
        video_id = youtube_link.split("youtu.be/")[1].split("?")[0]
    else:
        video_id = None

    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = fn_generate_summary(transcript_text, SUMMARY_PROMPT)
        st.markdown("## 📌 Detailed Notes:")
        st.write(summary)
