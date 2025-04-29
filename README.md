# Mock Interview Coach

An AI-powered mock interview platform that provides personalized interview practice, real-time feedback, and performance scoring.

## 🌟 Features

- **AI-Powered Interviews**: Dynamic question generation based on your resume and job description
- **Real-time Feedback**: Instant scoring and constructive feedback on your responses
- **Resume Analysis**: PDF resume parsing and context-aware question generation
- **Session Management**: Track your progress and review past interview sessions
- **Secure Authentication**: Google Sign-In integration for user authentication
- **Cloud Storage**: Secure storage for resumes and session data

## 🏗 Architecture

- **Frontend**: React + TypeScript + Vite
- **Backend**: Firebase Cloud Functions with Python
- **Authentication**: Firebase Authentication
- **Storage**: Firebase Cloud Storage
- **Database**: Firestore
- **AI Integration**: OpenAI GPT API

## 🚀 Live Demo

Visit [https://mock-interview-coach.web.app](https://mock-interview-coach.web.app) to try the application.

## 🛠 Local Development

### Prerequisites

- Node.js 16+ and npm
- Python 3.11+
- Firebase CLI (`npm install -g firebase-tools`)
- OpenAI API key
- Firebase project credentials

### Backend Setup

1. Navigate to the functions directory:
```bash
cd functions
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file in the functions directory:
```
OPENAI_API_KEY=your_openai_api_key_here
SERVICE_ACCOUNT_PATH=/path/to/your/service-account.json
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

3. Create `.env` file in the frontend directory:
```
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=mock-interview-coach.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=mock-interview-coach
VITE_FIREBASE_STORAGE_BUCKET=mock-interview-coach.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

4. Start development server:
```bash
npm run dev
```

## 📦 Deployment

### Frontend Deployment
```bash
cd frontend
npm run build
firebase deploy --only hosting
```

### Backend Deployment
```bash
cd functions
firebase deploy --only functions
```

## 🔒 Security Considerations

1. **Environment Variables**:
   - Never commit `.env` files
   - Keep API keys and credentials secure
   - Use different keys for development and production

2. **Firebase Security**:
   - Enable Google Authentication in Firebase Console
   - Configure proper Firestore security rules
   - Set up Storage security rules
   - Keep service account keys private

3. **API Security**:
   - All endpoints require authentication
   - Rate limiting is enabled
   - Request validation is implemented

## 📝 API Documentation

### Backend Functions

- `start-session`: Initiates a new interview session
  - URL: https://start-session-ofqboreeia-uc.a.run.app
  - Method: POST
  - Auth: Required

- `submit-response`: Submits and evaluates responses
  - URL: https://submit-response-ofqboreeia-uc.a.run.app
  - Method: POST
  - Auth: Required

- `get-session`: Retrieves session state
  - URL: https://get-session-ofqboreeia-uc.a.run.app
  - Method: GET
  - Auth: Required

- `end-session`: Concludes the session
  - URL: https://end-session-ofqboreeia-uc.a.run.app
  - Method: POST
  - Auth: Required

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT API
- Firebase for the backend infrastructure
- All contributors and users of the platform 