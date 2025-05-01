from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
import asyncio
from datetime import datetime

from .utils.pdf_parser import parse_pdf_to_text, clean_resume_text
from .utils.firebase_admin import require_auth
from .agents.base import InterviewerAgent, ScorerAgent, FeedbackAgent, QuestionRequest, ScoringRequest, FeedbackRequest

app = FastAPI(title="Mock Interview Coach MCP Orchestrator")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
interviewer_agent = InterviewerAgent()
scorer_agent = ScorerAgent()
feedback_agent = FeedbackAgent()

class InterviewResponse(BaseModel):
    question: str
    response: str
    score: float
    feedback: str
    timestamp: str

class SessionState(BaseModel):
    session_id: str
    user_id: str
    role: str
    resume_text: str
    job_description: str
    current_question: str
    response_history: List[InterviewResponse]

class SubmitResponseRequest(BaseModel):
    session_id: str
    response: str
    user_id: str

# In-memory session store
sessions: Dict[str, SessionState] = {}

@app.post("/start-session")
@require_auth
async def start_session(
    request: Request,
    role: str = Form(...),
    resume_url: str = Form(...),
    job_description: str = Form(...),
    user_id: str = Form(...)
) -> Dict[str, str]:
    """Start a new interview session and return the first question."""
    try:
        # Verify user_id matches the authenticated user
        if user_id != request.state.user_id:
            raise HTTPException(status_code=403, detail="User ID mismatch")
        
        # Get resume text from URL
        resume_text = await parse_pdf_from_url(resume_url)
        resume_text = clean_resume_text(resume_text)
        
        session_id = str(uuid.uuid4())
        
        # Get the first question from the interviewer agent
        question_request = QuestionRequest(
            role=role,
            resume_text=resume_text,
            job_description=job_description,
            previous_questions=[]
        )
        
        first_question = await interviewer_agent.generate_question(question_request)
        
        # Create and store new session state
        sessions[session_id] = SessionState(
            session_id=session_id,
            user_id=user_id,
            role=role,
            resume_text=resume_text,
            job_description=job_description,
            current_question=first_question,
            response_history=[]
        )
        
        return {
            "session_id": session_id,
            "question": first_question
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/next-question")
@require_auth
async def get_next_question(request: Request, session_id: str, user_id: str) -> Dict[str, str]:
    """Get the next interview question for a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Verify user owns this session
    if session.user_id != request.state.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    # Prepare previous questions
    previous_questions = [
        {"question": resp.question, "response": resp.response}
        for resp in session.response_history
    ]
    
    # Get next question
    question_request = QuestionRequest(
        role=session.role,
        resume_text=session.resume_text,
        job_description=session.job_description,
        previous_questions=previous_questions
    )
    
    next_question = await interviewer_agent.generate_question(question_request)
    session.current_question = next_question
    
    return {"question": next_question}

@app.post("/submit-response")
@require_auth
async def submit_response(request: Request, submit_request: SubmitResponseRequest) -> Dict[str, any]:
    """Submit a response and get the score and feedback."""
    if submit_request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[submit_request.session_id]
    
    # Verify user owns this session
    if session.user_id != request.state.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    current_question = session.current_question
    
    # Get score from scorer agent
    scoring_request = ScoringRequest(
        question=current_question,
        response=submit_request.response,
        role=session.role,
        job_description=session.job_description
    )
    score = await scorer_agent.score_response(scoring_request)
    
    # Get feedback from feedback agent
    feedback_request = FeedbackRequest(
        question=current_question,
        response=submit_request.response,
        score=score,
        role=session.role,
        job_description=session.job_description
    )
    feedback = await feedback_agent.generate_feedback(feedback_request)
    
    # Create response record
    response_record = InterviewResponse(
        question=current_question,
        response=submit_request.response,
        score=score,
        feedback=feedback,
        timestamp=datetime.utcnow().isoformat()
    )
    
    # Update session state
    session.response_history.append(response_record)
    
    return {
        "score": score,
        "feedback": feedback,
        "total_questions_answered": len(session.response_history)
    }

@app.get("/session/{session_id}")
@require_auth
async def get_session_state(request: Request, session_id: str, user_id: str) -> SessionState:
    """Get the current state of a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Verify user owns this session
    if session.user_id != request.state.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    return session

@app.on_event("startup")
async def startup_event():
    """Initialize agents when the application starts"""
    await interviewer_agent.initialize()
    await scorer_agent.initialize()
    await feedback_agent.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup agents when the application shuts down"""
    await interviewer_agent.cleanup()
    await scorer_agent.cleanup()
    await feedback_agent.cleanup() 