import { useState } from 'react'
import { Container, CssBaseline, ThemeProvider, createTheme } from '@mui/material'
import { SessionSetup } from './components/SessionSetup'
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
    <ThemeProvider theme={theme}>
      <CssBaseline />
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
    </ThemeProvider>
  )
}

export default App
