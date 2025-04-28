# AI Mock Interview System

An intelligent mock interview system that conducts personalized technical interviews based on your resume and desired job role. The system uses GPT-3.5 to generate relevant questions, provide real-time feedback, and score responses.

## Features

- Upload your resume (PDF format)
- Specify target job role and description
- Get personalized technical interview questions
- Receive immediate feedback and scoring
- Track interview progress and performance
- Modern, responsive web interface

## Tech Stack

### Backend
- FastAPI (Python web framework)
- OpenAI GPT-3.5
- PyPDF2 for PDF processing
- LangChain for AI orchestration

### Frontend
- React with TypeScript
- Material-UI (MUI) for components
- Axios for API communication
- Vite for build tooling

## Setup

### Prerequisites
- Python 3.11+
- Node.js 16+
- OpenAI API key

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv cursor_ai
source cursor_ai/bin/activate  # On Windows: cursor_ai\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_api_key_here
```

4. Start the backend server:
```bash
uvicorn mcp_orchestrator.app.main:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Project Structure

```
.
├── frontend/                # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/      # API services
│   │   └── types/         # TypeScript types
│   └── ...
├── mcp_orchestrator/       # FastAPI backend application
│   ├── app/
│   │   ├── agents/        # Interview agents
│   │   ├── utils/         # Utility functions
│   │   └── main.py        # FastAPI application
│   └── ...
├── requirements.txt        # Python dependencies
└── README.md
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License

MIT License - feel free to use this project for any purpose.

## Acknowledgments

- OpenAI for GPT-3.5
- FastAPI team for the excellent framework
- Material-UI team for the component library

## API Endpoints

### POST /start-session
Start a new interview session.
```json
{
    "role": "Machine Learning Scientist",
    "resume_text": "..."
}
```

### POST /next-question
Get the next interview question.
```json
{
    "session_id": "..."
}
```

### POST /submit-response
Submit a response and get feedback.
```json
{
    "session_id": "...",
    "response": "..."
}
```

### GET /session/{session_id}
Get the current state of a session.

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- OpenAPI specification: `http://localhost:8000/openapi.json` 