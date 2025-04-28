import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, CircularProgress } from '@mui/material';
import { InterviewResponse } from '../types/interview';
import { ExitToApp } from '@mui/icons-material';

interface InterviewSessionProps {
    currentQuestion: string;
    onSubmitResponse: (response: string) => Promise<void>;
    responseHistory: InterviewResponse[];
    isLoading: boolean;
    onEndSession: () => void;
}

export const InterviewSession: React.FC<InterviewSessionProps> = ({
    currentQuestion,
    onSubmitResponse,
    responseHistory,
    isLoading,
    onEndSession,
}) => {
    const [response, setResponse] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!response.trim()) {
            setError('Please provide a response');
            return;
        }

        try {
            await onSubmitResponse(response);
            setResponse('');
        } catch (err) {
            setError('Failed to submit response. Please try again.');
        }
    };

    return (
        <Box sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
            {/* Header with End Session button */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h5" component="h1">
                    Mock Interview Session
                </Typography>
                <Button
                    variant="outlined"
                    color="secondary"
                    onClick={onEndSession}
                    startIcon={<ExitToApp />}
                    disabled={isLoading}
                >
                    End Session
                </Button>
            </Box>

            {/* Current Question */}
            <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
                <Typography variant="h6" gutterBottom>
                    Current Question:
                </Typography>
                <Typography variant="body1" sx={{ mt: 2 }}>
                    {currentQuestion}
                </Typography>

                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
                    <TextField
                        fullWidth
                        label="Your Response"
                        value={response}
                        onChange={(e) => setResponse(e.target.value)}
                        multiline
                        rows={4}
                        required
                        disabled={isLoading}
                    />

                    {error && (
                        <Typography color="error" sx={{ mt: 2 }}>
                            {error}
                        </Typography>
                    )}

                    <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        fullWidth
                        sx={{ mt: 2 }}
                        disabled={isLoading}
                    >
                        {isLoading ? <CircularProgress size={24} /> : 'Submit Response'}
                    </Button>
                </Box>
            </Paper>

            {/* Response History */}
            {responseHistory.length > 0 && (
                <Paper elevation={3} sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        Previous Responses
                    </Typography>
                    {responseHistory.map((item, index) => (
                        <Box key={index} sx={{ mb: 4, pb: 2, borderBottom: index < responseHistory.length - 1 ? '1px solid #eee' : 'none' }}>
                            <Typography variant="subtitle1" color="primary" gutterBottom>
                                Question {index + 1}:
                            </Typography>
                            <Typography variant="body1" gutterBottom>
                                {item.question}
                            </Typography>

                            <Typography variant="subtitle1" color="primary" sx={{ mt: 2 }} gutterBottom>
                                Your Response:
                            </Typography>
                            <Typography variant="body1" gutterBottom>
                                {item.response}
                            </Typography>

                            <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Typography variant="subtitle2" color="primary">
                                    Score: {(item.score * 100).toFixed(0)}%
                                </Typography>
                            </Box>

                            <Typography variant="subtitle1" color="primary" sx={{ mt: 2 }} gutterBottom>
                                Feedback:
                            </Typography>
                            <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                                {item.feedback}
                            </Typography>
                        </Box>
                    ))}
                </Paper>
            )}
        </Box>
    );
}; 