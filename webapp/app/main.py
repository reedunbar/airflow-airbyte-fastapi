from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi


app = FastAPI()

@app.get("/")
async def read_root():
    return{"Hello": "World"}

@app.get("/test1")
async def read_root():
    return{"Hello": "World1"}

@app.get("/transcripts")
async def get_transcripts(video_id: str):
    try:
        transcripts = YouTubeTranscriptApi.get_transcript(video_id)
        return {"video_id": video_id, "transcripts": transcripts}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))