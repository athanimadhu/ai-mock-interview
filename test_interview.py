import asyncio
import json
from pathlib import Path
import httpx

# Sample data
SAMPLE_RESUME = """
JOHN DOE
Data Scientist / Machine Learning Engineer

EXPERIENCE
Senior Machine Learning Engineer | TechCorp (2020-Present)
- Developed and deployed production ML models using TensorFlow and PyTorch
- Improved model accuracy by 25% using advanced feature engineering
- Led a team of 3 engineers in developing real-time prediction systems

Data Scientist | AI Solutions Inc. (2018-2020)
- Built classification models for customer segmentation
- Implemented A/B testing framework for model evaluation
- Reduced processing time by 40% through optimization

SKILLS
- Languages: Python, R, SQL
- Frameworks: TensorFlow, PyTorch, scikit-learn
- Tools: Docker, Git, AWS
- Concepts: Deep Learning, NLP, Computer Vision

EDUCATION
M.S. Computer Science | Tech University (2018)
B.S. Mathematics | Science College (2016)
"""

SAMPLE_JOB = """
Senior Machine Learning Scientist

We're seeking an experienced Machine Learning Scientist to join our AI team. The ideal candidate will:
- Have strong experience in developing and deploying ML models
- Be proficient in Python and modern ML frameworks
- Understand both theoretical and practical aspects of ML
- Have experience with large-scale data processing

Requirements:
- 5+ years of ML experience
- Advanced degree in CS, Mathematics, or related field
- Expert in PyTorch or TensorFlow
- Strong communication skills
"""

async def test_interview():
    base_url = "http://localhost:8000"
    resume_path = "resume.pdf"  # Make sure to place your resume.pdf in the same directory
    
    async with httpx.AsyncClient() as client:
        # 1. Start session
        print("\n1. Starting interview session...")
        
        # Open and send the PDF file
        with open(resume_path, 'rb') as pdf_file:
            files = {
                'resume': ('resume.pdf', pdf_file, 'application/pdf')
            }
            data = {
                'role': 'Machine Learning Scientist',
                'job_description': SAMPLE_JOB
            }
            response = await client.post(f"{base_url}/start-session", files=files, data=data)
        
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data['session_id']
            print(f"Session started: {session_id}")
            print(f"First question: {session_data['question']}\n")
            
            # 2. Submit a response
            print("2. Submitting response to first question...")
            sample_response = """
            In my experience with machine learning frameworks, I've extensively used both TensorFlow and PyTorch. 
            At TechCorp, I implemented a deep learning model using TensorFlow for real-time image classification, 
            achieving 95% accuracy. I also used PyTorch for a natural language processing project where we built 
            a sentiment analysis model. I prefer PyTorch for research and prototyping due to its dynamic computational 
            graphs, while I find TensorFlow excellent for production deployment, especially with TensorFlow Serving.
            """
            
            response = await client.post(
                f"{base_url}/submit-response",
                json={"session_id": session_id, "response": sample_response}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Score: {result['score']}")
                print(f"Feedback: {result['feedback']}\n")
                
                # 3. Get next question
                print("3. Getting next question...")
                response = await client.post(
                    f"{base_url}/next-question",
                    params={"session_id": session_id}
                )
                
                if response.status_code == 200:
                    next_question = response.json()
                    print(f"Next question: {next_question['question']}\n")
                
                # 4. Get session state
                print("4. Getting session state...")
                response = await client.get(f"{base_url}/session/{session_id}")
                
                if response.status_code == 200:
                    session_state = response.json()
                    print("Session State:")
                    print(json.dumps(session_state, indent=2))
        else:
            print(f"Error starting session: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    asyncio.run(test_interview()) 