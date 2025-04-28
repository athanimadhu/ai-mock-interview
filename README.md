# Mock Interview Coach

A full-stack application that provides automated mock technical interviews using AI agents. The system includes an interviewer agent that generates questions, a scorer agent that evaluates responses, and a feedback agent that provides constructive feedback.

## Features

- Resume parsing and analysis
- Dynamic question generation based on candidate's profile
- Real-time response evaluation
- Detailed feedback and scoring
- Interactive interview sessions

## Tech Stack

- Backend: FastAPI, Python
- Frontend: React, TypeScript
- AI: OpenAI API
- PDF Processing: PyPDF2

## Project Structure

```
.
├── frontend/               # React frontend application
│   ├── public/            # Static files
│   └── src/               # Source code
│       ├── components/    # React components
│       ├── services/      # API services
│       └── types/         # TypeScript type definitions
│
├── mcp_orchestrator/      # FastAPI backend
│   └── app/
│       ├── agents/       # AI agent implementations
│       └── utils/        # Utility functions
│
└── requirements.txt       # Python dependencies
```

## Setup

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your OpenAI API key:
   - Required environment variable: `OPENAI_API_KEY`
   - Get your API key from [OpenAI's platform](https://platform.openai.com/api-keys)
4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

1. Start the backend server:
   ```bash
   cd mcp_orchestrator
   uvicorn app.main:app --reload
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm start
   ```

## API Endpoints

- `POST /start-session`: Start a new interview session
- `POST /next-question`: Get the next interview question
- `POST /submit-response`: Submit and evaluate a response
- `GET /session/{session_id}`: Get session state

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Acknowledgments

- OpenAI for GPT-3.5
- FastAPI team for the excellent framework
- Material-UI team for the component library

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- OpenAPI specification: `http://localhost:8000/openapi.json` 