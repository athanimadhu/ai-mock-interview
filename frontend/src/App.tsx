import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import { SessionSetup } from './components/SessionSetup';
import { useState } from 'react'
import { Container, CssBaseline, ThemeProvider, createTheme } from '@mui/material'
import { InterviewSession } from './components/InterviewSession'
import { api } from './services/api'
import { SessionState } from './types/interview'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
})

// Protected Route component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { currentUser, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!currentUser) {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
}

function App() {
  const [sessionState, setSessionState] = useState<SessionState | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSessionStart = async (role: string, resume: File, jobDescription: string) => {
    try {
      setIsLoading(true)
      const response = await api.startSession(role, resume, jobDescription)
      const state = await api.getSessionState(response.session_id)
      setSessionState(state)
    } catch (error) {
      console.error('Failed to start session:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmitResponse = async (response: string) => {
    if (!sessionState) return

    try {
      setIsLoading(true)
      await api.submitResponse({
        session_id: sessionState.session_id,
        response,
      })

      const updatedState = await api.getSessionState(sessionState.session_id)
      setSessionState(updatedState)
    } catch (error) {
      console.error('Failed to submit response:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const handleEndSession = () => {
    setSessionState(null)
    setIsLoading(false)
  }

  return (
    <Router>
      <AuthProvider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route 
              path="/" 
              element={
                <ProtectedRoute>
                  <Container>
                    {!sessionState ? (
                      <SessionSetup onSessionStart={handleSessionStart} />
                    ) : (
                      <InterviewSession
                        currentQuestion={sessionState.current_question}
                        onSubmitResponse={handleSubmitResponse}
                        responseHistory={sessionState.response_history}
                        isLoading={isLoading}
                        onEndSession={handleEndSession}
                      />
                    )}
                  </Container>
                </ProtectedRoute>
              } 
            />
          </Routes>
        </ThemeProvider>
      </AuthProvider>
    </Router>
  )
}

export default App
