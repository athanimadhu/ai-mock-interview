import React, { useRef } from 'react';
import { Box, Button, Typography } from '@mui/material';
import { axiosInstance } from '../services/api';
import { auth } from '../config/firebase';

interface AudioRecorderProps {
  onTranscriptionComplete: (text: string) => void;
  isRecording: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
}

const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onTranscriptionComplete,
  isRecording,
  onStartRecording,
  onStopRecording,
}) => {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        if (!auth.currentUser) {
          throw new Error('User must be authenticated to transcribe audio');
        }

        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        formData.append('user_id', auth.currentUser.uid);

        try {
          const response = await axiosInstance.post('/api/transcribe', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });

          if (response.data && response.data.text) {
            onTranscriptionComplete(response.data.text);
          } else {
            throw new Error('Invalid transcription response');
          }
        } catch (error) {
          console.error('Error during transcription:', error);
          alert('Failed to transcribe audio. Please try again or use text input.');
        }
      };

      mediaRecorder.start();
      onStartRecording();
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Unable to access microphone. Please check permissions and try again.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      onStopRecording();
    }
  };

  return (
    <Box sx={{ 
      margin: '1rem 0',
      textAlign: 'center'
    }}>
      <Button
        variant="contained"
        onClick={isRecording ? stopRecording : startRecording}
        sx={{
          bgcolor: isRecording ? '#ff4444' : '#4CAF50',
          '&:hover': {
            bgcolor: isRecording ? '#ff6666' : '#45a049',
            transform: 'scale(1.05)'
          },
          transition: 'all 0.3s ease',
          borderRadius: '25px',
          color: 'white',
          fontWeight: 'bold'
        }}
      >
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </Button>
      {isRecording && (
        <Typography
          sx={{
            marginTop: '0.5rem',
            color: '#ff4444',
            fontSize: '0.9rem'
          }}
        >
          Recording... Click 'Stop Recording' when finished
        </Typography>
      )}
    </Box>
  );
};

export default AudioRecorder; 