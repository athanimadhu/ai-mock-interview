# Firebase Functions Setup

This directory contains the Firebase Functions code for the Mock Interview Coach application.

## Prerequisites

1. Install Python 3.11 or later
2. Install Firebase CLI
3. Set up a Firebase project and enable Functions

## Local Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with:
```
OPENAI_API_KEY=your_openai_api_key_here
```

4. Run locally:
```bash
firebase emulators:start
```

## Deployment

1. Make sure you're logged in to Firebase:
```bash
firebase login
```

2. Deploy the functions:
```bash
firebase deploy --only functions
```

## Environment Variables

The following environment variables need to be set in your Firebase project:

- `OPENAI_API_KEY`: Your OpenAI API key

You can set these using:
```bash
firebase functions:config:set openai.api_key="your_key_here"
```

## Function Endpoints

- `POST /start-session`: Start a new interview session
- `POST /submit-response`: Submit a response to a question
- `GET /session/{session_id}`: Get session details
- `POST /end-session`: End an interview session

## Memory and Timeout Configuration

Functions are configured with:
- Memory: 1GB
- Timeout: 540 seconds

This is necessary for handling the OpenAI API calls and PDF processing. 