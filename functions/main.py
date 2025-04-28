# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app, storage, firestore
import functions_framework
from typing import Dict, Optional
import json
import os
from dotenv import load_dotenv

# Initialize Firebase Admin
app = initialize_app()
db = firestore.client()
bucket = storage.bucket()

# Load environment variables
load_dotenv()

# Import our existing agent classes
from mcp_orchestrator.app.agents.base import InterviewerAgent, ScorerAgent, FeedbackAgent
from mcp_orchestrator.app.utils.pdf_parser import parse_pdf_to_text, clean_resume_text

# Initialize agents
interviewer_agent = InterviewerAgent()
scorer_agent = ScorerAgent()
feedback_agent = FeedbackAgent()

@https_fn.on_request(
    cors=True,
    memory=1024,  # 1GB memory
    timeout_sec=540
)
def start_session(req: https_fn.Request) -> https_fn.Response:
    """Start a new interview session."""
    try:
        # Get the PDF file from the request
        if not req.files or 'resume' not in req.files:
            return https_fn.Response(
                json.dumps({"error": "No resume file provided"}),
                status=400,
                mimetype='application/json'
            )

        resume_file = req.files['resume']
        resume_text = parse_pdf_to_text(resume_file)
        cleaned_resume = clean_resume_text(resume_text)

        # Create a new session in Firestore
        session_ref = db.collection('sessions').document()
        session_data = {
            'resume_text': cleaned_resume,
            'current_question': None,
            'questions_asked': [],
            'responses': [],
            'scores': [],
            'feedback': [],
            'status': 'active'
        }
        session_ref.set(session_data)

        # Generate first question
        first_question = interviewer_agent.generate_question(cleaned_resume, [])

        # Update session with first question
        session_ref.update({
            'current_question': first_question,
            'questions_asked': [first_question]
        })

        return https_fn.Response(
            json.dumps({
                'session_id': session_ref.id,
                'question': first_question
            }),
            mimetype='application/json'
        )

    except Exception as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            mimetype='application/json'
        )

@https_fn.on_request(
    cors=True,
    memory=1024,  # 1GB memory
    timeout_sec=540
)
def submit_response(req: https_fn.Request) -> https_fn.Response:
    """Submit and evaluate a response."""
    try:
        data = req.get_json()
        session_id = data.get('session_id')
        response = data.get('response')

        if not session_id or not response:
            return https_fn.Response(
                json.dumps({"error": "Missing session_id or response"}),
                status=400,
                mimetype='application/json'
            )

        # Get session data
        session_ref = db.collection('sessions').document(session_id)
        session = session_ref.get()
        
        if not session.exists:
            return https_fn.Response(
                json.dumps({"error": "Session not found"}),
                status=404,
                mimetype='application/json'
            )

        session_data = session.to_dict()
        current_question = session_data['current_question']

        # Score the response
        score = scorer_agent.score_response(
            current_question,
            response,
            session_data['resume_text']
        )

        # Get feedback
        feedback = feedback_agent.generate_feedback(
            current_question,
            response,
            score,
            session_data['resume_text']
        )

        # Update session data
        session_data['responses'].append(response)
        session_data['scores'].append(score)
        session_data['feedback'].append(feedback)

        # Generate next question
        next_question = interviewer_agent.generate_question(
            session_data['resume_text'],
            session_data['questions_asked']
        )

        session_data['current_question'] = next_question
        session_data['questions_asked'].append(next_question)

        # Update Firestore
        session_ref.set(session_data)

        return https_fn.Response(
            json.dumps({
                'score': score,
                'feedback': feedback,
                'next_question': next_question
            }),
            mimetype='application/json'
        )

    except Exception as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            mimetype='application/json'
        )

@https_fn.on_request(cors=True)
def get_session(req: https_fn.Request) -> https_fn.Response:
    """Get the current state of a session."""
    try:
        session_id = req.args.get('session_id')
        if not session_id:
            return https_fn.Response(
                json.dumps({"error": "No session_id provided"}),
                status=400,
                mimetype='application/json'
            )

        session_ref = db.collection('sessions').document(session_id)
        session = session_ref.get()

        if not session.exists:
            return https_fn.Response(
                json.dumps({"error": "Session not found"}),
                status=404,
                mimetype='application/json'
            )

        return https_fn.Response(
            json.dumps(session.to_dict()),
            mimetype='application/json'
        )

    except Exception as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            mimetype='application/json'
        )

@https_fn.on_request(cors=True)
def end_session(req: https_fn.Request) -> https_fn.Response:
    """End an interview session and generate final analysis."""
    try:
        data = req.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return https_fn.Response(
                json.dumps({"error": "No session_id provided"}),
                status=400,
                mimetype='application/json'
            )

        session_ref = db.collection('sessions').document(session_id)
        session = session_ref.get()

        if not session.exists:
            return https_fn.Response(
                json.dumps({"error": "Session not found"}),
                status=404,
                mimetype='application/json'
            )

        session_data = session.to_dict()

        # Generate final analysis
        analysis = {
            'questions': session_data['questions_asked'],
            'responses': session_data['responses'],
            'scores': session_data['scores'],
            'feedback': session_data['feedback'],
            'average_score': sum(session_data['scores']) / len(session_data['scores']) if session_data['scores'] else 0
        }

        # Store analysis in Firebase Storage
        analysis_blob = bucket.blob(f'analysis/{session_id}.json')
        analysis_blob.upload_from_string(
            json.dumps(analysis),
            content_type='application/json'
        )

        # Update session status
        session_ref.update({
            'status': 'completed',
            'analysis_url': analysis_blob.public_url
        })

        return https_fn.Response(
            json.dumps({
                'status': 'completed',
                'analysis_url': analysis_blob.public_url,
                'analysis': analysis
            }),
            mimetype='application/json'
        )

    except Exception as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            mimetype='application/json'
        )