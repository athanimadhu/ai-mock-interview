from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pydantic import BaseModel
from ..utils.openai_client import OpenAIClient

class QuestionRequest(BaseModel):
    role: str
    resume_text: str
    job_description: str
    previous_questions: List[Dict[str, str]] = []

class ScoringRequest(BaseModel):
    question: str
    response: str
    role: str
    job_description: str

class FeedbackRequest(BaseModel):
    question: str
    response: str
    score: float
    role: str
    job_description: str

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self):
        self.openai_client = None
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize any resources needed by the agent"""
        self.openai_client = OpenAIClient()
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup any resources used by the agent"""
        self.openai_client = None

class InterviewerAgent(BaseAgent):
    """Agent responsible for generating interview questions"""
    
    async def initialize(self) -> None:
        await super().initialize()
    
    async def cleanup(self) -> None:
        await super().cleanup()
    
    async def generate_question(self, request: QuestionRequest) -> str:
        """
        Generate the next interview question based on the role, resume, and history.
        
        Args:
            request (QuestionRequest): Contains role, resume text, and question history
            
        Returns:
            str: The next interview question
        """
        return await self.openai_client.generate_interview_question(
            role=request.role,
            resume_text=request.resume_text,
            job_description=request.job_description,
            previous_qa=request.previous_questions
        )

class ScorerAgent(BaseAgent):
    """Agent responsible for scoring responses"""
    
    async def initialize(self) -> None:
        await super().initialize()
    
    async def cleanup(self) -> None:
        await super().cleanup()
    
    async def score_response(self, request: ScoringRequest) -> float:
        """
        Score the candidate's response.
        
        Args:
            request (ScoringRequest): Contains question and response
            
        Returns:
            float: Score between 0 and 1
        """
        return await self.openai_client.score_response(
            question=request.question,
            response=request.response,
            role=request.role,
            job_description=request.job_description
        )

class FeedbackAgent(BaseAgent):
    """Agent responsible for providing feedback"""
    
    async def initialize(self) -> None:
        await super().initialize()
    
    async def cleanup(self) -> None:
        await super().cleanup()
    
    async def generate_feedback(self, request: FeedbackRequest) -> str:
        """
        Generate feedback based on the response and score.
        
        Args:
            request (FeedbackRequest): Contains question, response, and score
            
        Returns:
            str: Detailed feedback
        """
        return await self.openai_client.generate_feedback(
            question=request.question,
            response=request.response,
            score=request.score,
            role=request.role
        ) 