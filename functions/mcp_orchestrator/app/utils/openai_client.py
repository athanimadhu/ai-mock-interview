from typing import List, Dict, Any
import openai
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-3.5-turbo"  # Using more cost-effective model
    
    async def generate_interview_question(self, role: str, resume_text: str, job_description: str, previous_qa: List[Dict[str, str]]) -> str:
        """Generate a relevant interview question based on context."""
        
        # Create a more focused prompt for GPT-3.5
        prompt = f"""Role: Expert Technical Interviewer for {role} position

Job Description Summary:
{job_description[:500]}  # Limiting context length for cost efficiency

Key Resume Points:
{resume_text[:500]}  # Limiting context length for cost efficiency

Task: Generate a specific, technical interview question that:
1. Tests both theoretical knowledge and practical skills
2. Relates to the candidate's background
3. Aligns with job requirements
4. Is clear and concise

Previous Questions Asked:
{' '.join([qa['question'] for qa in previous_qa[-2:]])}  # Only including last 2 questions for context"""

        conversation = [
            {"role": "system", "content": "You are an expert technical interviewer. Generate only the next interview question without any additional text or explanation."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=conversation,
            temperature=0.7,
            max_tokens=100  # Reduced token limit for cost efficiency
        )
        
        return response.choices[0].message.content.strip()
    
    async def score_response(self, question: str, response: str, role: str, job_description: str) -> float:
        """Score the candidate's response."""
        
        prompt = f"""Question: {question}

Candidate Response: {response}

Evaluate the response for a {role} position based on:
1. Technical Accuracy (40%)
2. Clarity (30%)
3. Practical Understanding (30%)

Return only a single number between 0 and 1 representing the total score."""

        conversation = [
            {"role": "system", "content": "You are an expert technical evaluator. Provide only a numerical score between 0 and 1."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=conversation,
            temperature=0.3,
            max_tokens=10  # Very limited tokens since we only need a number
        )
        
        try:
            score = float(response.choices[0].message.content.strip())
            return min(max(score, 0.0), 1.0)  # Ensure score is between 0 and 1
        except ValueError:
            return 0.5  # Default score if parsing fails
    
    async def generate_feedback(self, question: str, response: str, score: float, role: str) -> str:
        """Generate detailed feedback for the response."""
        
        prompt = f"""Question: {question}

Response: {response}

Score: {score:.2%}

Provide brief, specific feedback that:
1. Highlights one key strength
2. Identifies one main area for improvement
3. Gives one actionable suggestion
4. Maintains a constructive tone

Keep feedback under 100 words."""

        conversation = [
            {"role": "system", "content": "You are an expert technical interviewer providing concise, actionable feedback."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=conversation,
            temperature=0.7,
            max_tokens=150  # Reduced for cost efficiency
        )
        
        return response.choices[0].message.content.strip() 