# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.quiz_generation_route import router

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://6dd3bmv5-5173.inc1.devtunnels.ms", "http://127.0.0.1:5173","https://youtube-quiz-generator-sage.vercel.app","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the quiz generation router
app.include_router(router)
