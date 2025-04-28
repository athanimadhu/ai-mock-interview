import axios from 'axios';
import { StartSessionResponse, SubmitResponseRequest, SubmitResponseResponse, SessionState } from '../types/interview';

const API_BASE_URL = 'http://localhost:8000';

const axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Accept': 'application/json',
    },
});

// Add response interceptor for better error handling
axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        throw error;
    }
);

export const api = {
    startSession: async (role: string, resume: File, jobDescription: string): Promise<StartSessionResponse> => {
        try {
            const formData = new FormData();
            formData.append('role', role);
            formData.append('resume', resume);
            formData.append('job_description', jobDescription);

            const response = await axiosInstance.post<StartSessionResponse>('/start-session', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            console.error('Start Session Error:', error);
            throw error;
        }
    },

    submitResponse: async (request: SubmitResponseRequest): Promise<SubmitResponseResponse> => {
        const response = await axiosInstance.post<SubmitResponseResponse>('/submit-response', request);
        return response.data;
    },

    getNextQuestion: async (sessionId: string): Promise<{ question: string }> => {
        const response = await axiosInstance.post<{ question: string }>('/next-question', null, {
            params: { session_id: sessionId },
        });
        return response.data;
    },

    getSessionState: async (sessionId: string): Promise<SessionState> => {
        const response = await axiosInstance.get<SessionState>(`/session/${sessionId}`);
        return response.data;
    },
}; 