import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, Alert } from '@mui/material';
import { CloudUpload } from '@mui/icons-material';

interface SessionSetupProps {
    onSessionStart: (role: string, resume: File, jobDescription: string) => Promise<void>;
}

export const SessionSetup: React.FC<SessionSetupProps> = ({ onSessionStart }) => {
    const [role, setRole] = useState('');
    const [resume, setResume] = useState<File | null>(null);
    const [jobDescription, setJobDescription] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        if (!role || !resume || !jobDescription) {
            setError('Please fill in all fields');
            setIsLoading(false);
            return;
        }

        try {
            await onSessionStart(role, resume, jobDescription);
        } catch (err: any) {
            console.error('Session Setup Error:', err);
            setError(
                err.response?.data?.detail || 
                err.message || 
                'Failed to start session. Please try again.'
            );
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Paper elevation={3} sx={{ p: 4, maxWidth: 600, mx: 'auto', mt: 4 }}>
            <Typography variant="h5" component="h2" gutterBottom>
                Start Mock Interview Session
            </Typography>
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                <TextField
                    fullWidth
                    label="Job Role"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    margin="normal"
                    required
                    disabled={isLoading}
                />
                
                <Box sx={{ mt: 2, mb: 2 }}>
                    <input
                        accept=".pdf"
                        style={{ display: 'none' }}
                        id="resume-file"
                        type="file"
                        onChange={(e) => setResume(e.target.files?.[0] || null)}
                        disabled={isLoading}
                    />
                    <label htmlFor="resume-file">
                        <Button
                            variant="outlined"
                            component="span"
                            startIcon={<CloudUpload />}
                            fullWidth
                            disabled={isLoading}
                        >
                            {resume ? resume.name : 'Upload Resume (PDF)'}
                        </Button>
                    </label>
                </Box>

                <TextField
                    fullWidth
                    label="Job Description"
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    margin="normal"
                    required
                    multiline
                    rows={4}
                    disabled={isLoading}
                />

                {error && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                        {error}
                    </Alert>
                )}

                <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    fullWidth
                    sx={{ mt: 3 }}
                    disabled={isLoading}
                >
                    {isLoading ? 'Starting Session...' : 'Start Interview'}
                </Button>
            </Box>
        </Paper>
    );
}; 