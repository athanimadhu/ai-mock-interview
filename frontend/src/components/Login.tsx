import { Button, Container, Typography, Box } from '@mui/material';
import { Google as GoogleIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

export default function Login() {
  const { signInWithGoogle, currentUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (currentUser) {
      navigate('/');
    }
  }, [currentUser, navigate]);

  const handleGoogleSignIn = async () => {
    try {
      await signInWithGoogle();
      // Navigation will be handled by the useEffect above
    } catch (error) {
      console.error('Failed to sign in:', error);
      // You might want to show an error message to the user here
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 3
        }}
      >
        <Typography component="h1" variant="h4">
          Mock Interview Coach
        </Typography>
        
        <Typography variant="body1" color="text.secondary" align="center">
          Sign in to start practicing your interview skills with AI-powered feedback
        </Typography>

        <Button
          variant="contained"
          startIcon={<GoogleIcon />}
          onClick={handleGoogleSignIn}
          size="large"
        >
          Sign in with Google
        </Button>
      </Box>
    </Container>
  );
} 