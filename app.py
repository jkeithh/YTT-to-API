from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import yt_dlp as youtube_dl
from deepgram import Deepgram
import asyncio
import os

# Initialize FastAPI app
app = FastAPI()

# API Key for Deepgram
DEEPGRAM_API_KEY = 'a0b3e0caed8808979462331899c72fe79eda5ba8'
dg_client = Deepgram(DEEPGRAM_API_KEY)

def extract_audio(url: str):
    """Extract audio from YouTube URL using yt-dlp."""
    if os.path.exists("audio.mp3"):
        os.remove("audio.mp3")
    ydl_opts = {'format': 'bestaudio', 'outtmpl': 'audio.mp3'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'audio.mp3'

async def transcribe_audio(file_path: str) -> str:
    """Transcribe audio using Deepgram asynchronously."""
    with open(file_path, 'rb') as audio:
        source = {'buffer': audio, 'mimetype': 'audio/mpeg'}
        response = await dg_client.transcription.prerecorded(
            source, {'punctuate': True}
        )
    return response['results']['channels'][0]['alternatives'][0]['transcript']

def run_async_function(func, *args):
    """Helper to run async code in a synchronous context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(func(*args))

class YouTubeURL(BaseModel):
    url: str

@app.post("/transcribe/")
def transcribe_youtube_video(data: YouTubeURL):
    """Endpoint to extract audio and transcribe from YouTube."""
    try:
        audio_file = extract_audio(data.url)
        transcript = run_async_function(transcribe_audio, audio_file)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
