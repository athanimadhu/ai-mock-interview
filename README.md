# Mock Interview Coach

A full-stack application that provides AI-powered mock interviews, real-time feedback, and scoring.

## Project Structure

- `frontend/`: React frontend application
- `functions/`: Firebase Cloud Functions backend
- `mcp_orchestrator/`: Local development server for testing
- `public/`: Static assets

## Features

- AI-powered interview questions based on resume
- Real-time response scoring and feedback
- Session management and progress tracking
- PDF resume parsing and analysis

## Local Development

### Backend (Firebase Functions)

See [functions/README.md](functions/README.md) for detailed setup instructions.

### Frontend

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
npm start
```

## Environment Setup

1. Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

2. Set up Firebase:
   - Create a new Firebase project
   - Enable Cloud Functions
   - Configure Firebase credentials

## Deployment

### Frontend

```bash
cd frontend
npm run build
firebase deploy --only hosting
```

### Backend

```bash
cd functions
firebase deploy --only functions
```

## Testing

Run the test suite:
```bash
python -m pytest test_interview.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- OpenAPI specification: `http://localhost:8000/openapi.json` 