import axios from 'axios';
import { StartSessionResponse, SubmitResponseRequest, SubmitResponseResponse, SessionState } from '../types/interview';
import { auth } from '../config/firebase';
import { firebaseStorage } from './firebase';

// Use relative paths since we're using Firebase Hosting proxy
const axiosInstance = axios.create({
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
axiosInstance.interceptors.request.use(async (config) => {
    if (!auth.currentUser) {
        console.error('No authenticated user!');
        throw new Error('User must be authenticated to make API requests');
    }
    const token = await auth.currentUser.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
    // Only log that authentication is being set, not the actual token
    console.log('Authentication: Token set (redacted for security)');
    return config;
});

// Add response interceptor for better error handling
axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', {
            message: error.message,
            response: error.response?.data,
            status: error.response?.status,
            url: error.config?.url
        });
        throw error;
    }
);

export const api = {
    startSession: async (role: string, resume: File, jobDescription: string): Promise<StartSessionResponse> => {
        try {
            if (!auth.currentUser) {
                throw new Error('User must be authenticated to start a session');
            }

            // Upload resume to Firebase Storage
            const resumeUrl = await firebaseStorage.uploadResume(resume);
            console.log('Resume uploaded successfully:', resumeUrl);

            // Create session with resume URL
            const response = await axiosInstance.post<StartSessionResponse>('/api/start-session', {
                role,
                resume_url: resumeUrl,
                job_description: jobDescription,
                user_id: auth.currentUser.uid
            });
            
            console.log('Session started successfully:', response.data);
            return response.data;
        } catch (error) {
            console.error('Start Session Error:', error);
            throw error;
        }
    },

    submitResponse: async (request: SubmitResponseRequest): Promise<SubmitResponseResponse> => {
        if (!auth.currentUser) {
            throw new Error('User must be authenticated to submit a response');
        }
        // Log the payload for debugging
        console.log('Payload to backend:', request);
        const response = await axiosInstance.post<SubmitResponseResponse>('/api/submit-response', {
            session_id: request.session_id,
            response: request.response
        });
        return response.data;
    },

    getNextQuestion: async (sessionId: string): Promise<{ question: string }> => {
        if (!auth.currentUser) {
            throw new Error('User must be authenticated to get next question');
        }
        const response = await axiosInstance.post<{ question: string }>('/api/next-question', {
            user_id: auth.currentUser.uid
        }, {
            params: { session_id: sessionId },
        });
        return response.data;
    },

    getSessionState: async (sessionId: string): Promise<SessionState> => {
        if (!auth.currentUser) {
            throw new Error('User must be authenticated to get session state');
        }
        const response = await axiosInstance.get<SessionState>(`/api/get-session`, {
            params: { session_id: sessionId, user_id: auth.currentUser.uid }
        });
        console.log('Fetched session state:', response.data);
        if (!response.data.session_id) {
            response.data.session_id = sessionId;
        }
        return response.data;
    },
};

export { axiosInstance }; 