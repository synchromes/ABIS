from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import logging

from .core.config import settings
from .core.database import init_db, get_db
from .api import auth, interviews, settings as settings_api
from .websocket.interview_handler import manager
from .models.interview import TranscriptEntry, EmotionLog
from .models.indicator import InterviewIndicator, InterviewAssessment

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# Ensure interview handler logger is also INFO level
interview_logger = logging.getLogger('app.websocket.interview_handler')
interview_logger.setLevel(logging.INFO)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered interview assistant system for ASN candidate selection"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(interviews.router, prefix="/api/interviews", tags=["Interviews"])
app.include_router(settings_api.router, prefix="/api", tags=["Settings"])

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Check AI availability
    from .websocket.interview_handler import AI_AVAILABLE
    if AI_AVAILABLE:
        logger.info("=" * 60)
        logger.info("AI STATUS: REAL AI SERVICES LOADED")
        logger.info("=" * 60)
    else:
        logger.warning("=" * 60)
        logger.warning("AI STATUS: USING MOCK SERVICES")
        logger.warning("=" * 60)
    
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        logger.warning("Continue without database - some features may not work")
        logger.warning("Please run: mysql -u root -p < database/init.sql")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application")

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.websocket("/ws/interview/{interview_id}")
async def websocket_interview_endpoint(
    websocket: WebSocket,
    interview_id: int,
    db: Session = Depends(get_db)
):
    await manager.connect(websocket, interview_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            logger.info(f"[WS] Received message type: {message_type}")
            
            if message_type == "video_frame":
                logger.info(f"[WS] Processing video frame for interview {interview_id}")
                frame_data = data.get("data")
                await manager.process_video_frame(interview_id, frame_data)
            
            elif message_type == "audio_chunk":
                logger.info(f"[WS] Processing audio chunk for interview {interview_id}")
                audio_data = data.get("data")
                await manager.process_audio_chunk(interview_id, audio_data)
            
            elif message_type == "save_transcript":
                transcript_data = data.get("data")
                transcript_entry = TranscriptEntry(
                    interview_id=interview_id,
                    speaker=transcript_data.get("speaker", "Candidate"),
                    text=transcript_data.get("text"),
                    timestamp=transcript_data.get("timestamp"),
                    confidence=transcript_data.get("confidence"),
                    emotion_detected=transcript_data.get("emotion_detected"),
                    sentiment_score=transcript_data.get("sentiment_score")
                )
                db.add(transcript_entry)
                db.commit()
            
            elif message_type == "save_emotion":
                emotion_data = data.get("data")
                logger.info(f"[WS] Saving emotion for interview {interview_id}: {emotion_data.get('facial_emotion')}")
                emotion_log = EmotionLog(
                    interview_id=interview_id,
                    timestamp=emotion_data.get("timestamp"),
                    facial_emotion=emotion_data.get("facial_emotion"),
                    facial_confidence=emotion_data.get("facial_confidence"),
                    speech_emotion=emotion_data.get("speech_emotion"),
                    speech_confidence=emotion_data.get("speech_confidence"),
                    emotion_scores=emotion_data.get("emotion_scores")
                )
                db.add(emotion_log)
                db.commit()
                logger.info(f"[WS] Emotion saved to database")
            
            elif message_type == "get_analysis":
                analysis = await manager.get_current_analysis(interview_id)
                await manager.send_message(interview_id, {
                    "type": "analysis_update",
                    "data": analysis
                })
            
            elif message_type == "ping":
                await manager.send_message(interview_id, {
                    "type": "pong",
                    "data": {"timestamp": data.get("timestamp")}
                })
            
            else:
                logger.warning(f"[WS] Unknown message type: {message_type}")
    
    except WebSocketDisconnect:
        manager.disconnect(interview_id, db=db)
        logger.info(f"WebSocket disconnected for interview {interview_id}")
    except Exception as e:
        logger.error(f"[WS] WebSocket error: {e}", exc_info=True)
        manager.disconnect(interview_id, db=db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
