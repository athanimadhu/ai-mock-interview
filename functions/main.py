# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app, storage, firestore, auth
import functions_framework
from typing import Dict, Optional
import json
import os
from dotenv import load_dotenv
import requests
import asyncio

# Initialize Firebase Admin
app = initialize_app()
db = firestore.client()
bucket = storage.bucket()

# Load environment variables
load_dotenv()

# Import our existing agent classes
from mcp_orchestrator.app.agents.base import InterviewerAgent, ScorerAgent, FeedbackAgent, QuestionRequest, ScoringRequest, FeedbackRequest
from mcp_orchestrator.app.utils.pdf_parser import parse_pdf_to_text, clean_resume_text

# Initialize agents
interviewer_agent = InterviewerAgent()
scorer_agent = ScorerAgent()
feedback_agent = FeedbackAgent()

def verify_auth_token(req: https_fn.Request) -> str:
    """Verify Firebase auth token from request headers."""
    if not req.headers.get('Authorization'):
        raise ValueError('No authorization token provided')
    
    token = req.headers.get('Authorization').split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        raise ValueError('Invalid authorization token')

@https_fn.on_request(memory=1024,timeout_sec=540)
def start_session(req: https_fn.Request) -> https_fn.Response:
    """Start a new interview session."""
    try:
        # Verify auth token
        user_id = verify_auth_token(req)

        # Get the data from the JSON request
        if not req.is_json:
            return https_fn.Response(
                json.dumps({"error": "Request must be JSON"}),
                status=400,
                content_type='application/json'
            )

        data = req.get_json()
        resume_url = data.get('resume_url')
        role = data.get('role')
        job_description = data.get('job_description')

        if not all([resume_url, role, job_description]):
            return https_fn.Response(
                json.dumps({"error": "Missing required fields: resume_url, role, job_description"}),
                status=400,
                content_type='application/json'
            )

        # Download and process the resume
        try:
            response = requests.get(resume_url)
            response.raise_for_status()
            resume_text = parse_pdf_to_text(response.content)
            cleaned_resume = clean_resume_text(resume_text)
        except Exception as e:
            return https_fn.Response(
                json.dumps({"error": f"Failed to process resume: {str(e)}"}),
                status=400,
                content_type='application/json'
            )

        # Create a new session in Firestore
        session_ref = db.collection('sessions').document()
        session_data = {
            'user_id': user_id,  # Use verified user_id from token
            'role': role,
            'job_description': job_description,
            'resume_text': cleaned_resume,
            'current_question': None,
            'questions_asked': [],
            'responses': [],
            'scores': [],
            'feedback': [],
            'response_history': [],  # Add this field for frontend compatibility
            'status': 'active'
        }
        session_ref.set(session_data)

        async def generate_first_question():
            # Initialize the interviewer agent
            await interviewer_agent.initialize()

            # Generate first question
            question_request = QuestionRequest(
                role=role,
                resume_text=cleaned_resume,
                job_description=job_description,
                previous_questions=[]
            )
            first_question = await interviewer_agent.generate_question(question_request)

            # Cleanup the agent
            await interviewer_agent.cleanup()
            return first_question

        # Run the async code in a synchronous context
        first_question = asyncio.run(generate_first_question())

        # Update session with first question
        session_ref.update({
            'current_question': first_question,
            'questions_asked': [first_question],
            'response_history': []  # Initialize the response history array
        })

        return https_fn.Response(
            json.dumps({
                'session_id': session_ref.id,
                'question': first_question
            }),
            content_type='application/json'
        )

    except ValueError as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=401,
            content_type='application/json'
        )
    except Exception as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            content_type='application/json'
        )

@https_fn.on_request(memory=1024,timeout_sec=540)
def submit_response(req: https_fn.Request) -> https_fn.Response:
    """Submit and evaluate a response."""
    try:
        # Verify auth token
        user_id = verify_auth_token(req)

        data = req.get_json()
        session_id = data.get('session_id')
        response_text = data.get('response')

        if not session_id or not response_text:
            return https_fn.Response(
                json.dumps({"error": "Missing session_id or response"}),
                status=400,
                content_type='application/json'
            )

        # Get session data
        session_ref = db.collection('sessions').document(session_id)
        session = session_ref.get()
        
        if not session.exists:
            return https_fn.Response(
                json.dumps({"error": "Session not found"}),
                status=404,
                content_type='application/json'
            )

        session_data = session.to_dict()
        
        # Verify user owns this session
        if session_data['user_id'] != user_id:
            return https_fn.Response(
                json.dumps({"error": "Unauthorized access to session"}),
                status=403,
                content_type='application/json'
            )

        current_question = session_data['current_question']

        async def process_response():
            # Initialize agents
            await scorer_agent.initialize()
            await feedback_agent.initialize()
            await interviewer_agent.initialize()

            # Score the response
            scoring_request = ScoringRequest(
                question=current_question,
                response=response_text,
                role=session_data['role'],
                job_description=session_data['job_description']
            )
            score = await scorer_agent.score_response(scoring_request)

            # Get feedback
            feedback_request = FeedbackRequest(
                question=current_question,
                response=response_text,
                score=score,
                role=session_data['role'],
                job_description=session_data['job_description']
            )
            feedback = await feedback_agent.generate_feedback(feedback_request)

            # Generate next question
            question_request = QuestionRequest(
                role=session_data['role'],
                resume_text=session_data['resume_text'],
                job_description=session_data['job_description'],
                previous_questions=session_data['questions_asked']
            )
            next_question = await interviewer_agent.generate_question(question_request)

            # Cleanup agents
            await scorer_agent.cleanup()
            await feedback_agent.cleanup()
            await interviewer_agent.cleanup()

            return score, feedback, next_question

        # Run the async code in a synchronous context
        score, feedback, next_question = asyncio.run(process_response())

        # Update session data
        session_data['responses'].append(response_text)
        session_data['scores'].append(score)
        session_data['feedback'].append(feedback)
        session_data['current_question'] = next_question
        session_data['questions_asked'].append(next_question)

        # Update response history for frontend
        session_data['response_history'].append({
            'question': current_question,
            'response': response_text,
            'score': score,
            'feedback': feedback,
            'timestamp': firestore.SERVER_TIMESTAMP
        })

        # Update Firestore
        session_ref.set(session_data)

        return https_fn.Response(
            json.dumps({
                'score': score,
                'feedback': feedback,
                'next_question': next_question
            }),
            content_type='application/json'
        )

    except ValueError as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=401,
            content_type='application/json'
        )
    except Exception as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            content_type='application/json'
        )

@https_fn.on_request(memory=1024,timeout_sec=540)
def get_session(req: https_fn.Request) -> https_fn.Response:
    """Get the current state of a session."""
    try:
        # Verify auth token
        user_id = verify_auth_token(req)

        session_id = req.args.get('session_id')
        if not session_id:
            return https_fn.Response(
                json.dumps({"error": "No session_id provided"}),
                status=400,
                content_type='application/json'
            )

        session_ref = db.collection('sessions').document(session_id)
        session = session_ref.get()

        if not session.exists:
            return https_fn.Response(
                json.dumps({"error": "Session not found"}),
                status=404,
                content_type='application/json'
            )

        session_data = session.to_dict()
        
        # Verify user owns this session
        if session_data['user_id'] != user_id:
            return https_fn.Response(
                json.dumps({"error": "Unauthorized access to session"}),
                status=403,
                content_type='application/json'
            )

        return https_fn.Response(
            json.dumps(session_data),
            content_type='application/json'
        )

    except ValueError as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=401,
            content_type='application/json'
        )
    except Exception as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            content_type='application/json'
        )

@https_fn.on_request(memory=1024,timeout_sec=540)
def end_session(req: https_fn.Request) -> https_fn.Response:
    """End an interview session and generate final analysis."""
    try:
        # Verify auth token
        user_id = verify_auth_token(req)

        data = req.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return https_fn.Response(
                json.dumps({"error": "No session_id provided"}),
                status=400,
                content_type='application/json'
            )

        session_ref = db.collection('sessions').document(session_id)
        session = session_ref.get()

        if not session.exists:
            return https_fn.Response(
                json.dumps({"error": "Session not found"}),
                status=404,
                content_type='application/json'
            )

        session_data = session.to_dict()
        
        # Verify user owns this session
        if session_data['user_id'] != user_id:
            return https_fn.Response(
                json.dumps({"error": "Unauthorized access to session"}),
                status=403,
                content_type='application/json'
            )

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
            content_type='application/json'
        )

    except ValueError as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=401,
            content_type='application/json'
        )
    except Exception as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            content_type='application/json'
        )