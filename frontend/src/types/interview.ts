export interface InterviewResponse {
    question: string;
    response: string;
    score: number;
    feedback: string;
    timestamp: string;
}

export interface SessionState {
    session_id: string;
    role: string;
    resume_text: string;
    job_description: string;
    current_question: string;
    response_history: InterviewResponse[];
}

export interface StartSessionResponse {
    session_id: string;
    question: string;
}

export interface SubmitResponseRequest {
    session_id: string;
    response: string;
}

export interface SubmitResponseResponse {
    score: number;
    feedback: string;
    total_questions_answered: number;
} 