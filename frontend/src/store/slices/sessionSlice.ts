import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

export interface Session {
  id: number
  name: string
  description: string | null
  location_id: number
  start_time: string | null
  end_time: string | null
  status: string
  created_by: number
  created_at: string
  updated_at: string
}

interface SessionState {
  sessions: Session[]
  currentSession: Session | null
  loading: boolean
  error: string | null
  total: number
}

const initialState: SessionState = {
  sessions: [],
  currentSession: null,
  loading: false,
  error: null,
  total: 0,
}

export const fetchSessions = createAsyncThunk(
  'sessions/fetchSessions',
  async (params: { status?: string; location_id?: number }) => {
    const response = await api.get('/sessions', { params })
    return response.data
  }
)

export const createSession = createAsyncThunk(
  'sessions/createSession',
  async (session: Omit<Session, 'id' | 'created_by' | 'created_at' | 'updated_at'>) => {
    const response = await api.post('/sessions', session)
    return response.data
  }
)

const transitionSession = (action: string, path: string) => createAsyncThunk(
  `sessions/${action}`,
  async (sessionId: number) => {
    const response = await api.post(`/sessions/${sessionId}/${path}`)
    return response.data
  }
)

export const startSession = transitionSession('startSession', 'start')
export const pauseSession = transitionSession('pauseSession', 'pause')
export const resumeSession = transitionSession('resumeSession', 'resume')
export const completeCounting = transitionSession('completeCounting', 'counting-complete')
export const startReconciliation = transitionSession('startReconciliation', 'reconcile')
export const completeSession = transitionSession('completeSession', 'complete')

const sessionSlice = createSlice({
  name: 'sessions',
  initialState,
  reducers: {
    setCurrentSession: (state, action) => {
      state.currentSession = action.payload
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSessions.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchSessions.fulfilled, (state, action) => {
        state.loading = false
        state.sessions = action.payload.items
        state.total = action.payload.total
      })
      .addCase(fetchSessions.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch sessions'
      })
      .addCase(createSession.fulfilled, (state, action) => {
        state.sessions.push(action.payload)
      })
      .addCase(startSession.fulfilled, (state, action) => {
        const index = state.sessions.findIndex(s => s.id === action.payload.id)
        if (index !== -1) state.sessions[index] = action.payload
      })
      .addCase(pauseSession.fulfilled, (state, action) => {
        const index = state.sessions.findIndex(s => s.id === action.payload.id)
        if (index !== -1) state.sessions[index] = action.payload
      })
      .addCase(resumeSession.fulfilled, (state, action) => {
        const index = state.sessions.findIndex(s => s.id === action.payload.id)
        if (index !== -1) state.sessions[index] = action.payload
      })
      .addCase(completeCounting.fulfilled, (state, action) => {
        const index = state.sessions.findIndex(s => s.id === action.payload.id)
        if (index !== -1) state.sessions[index] = action.payload
      })
      .addCase(startReconciliation.fulfilled, (state, action) => {
        const index = state.sessions.findIndex(s => s.id === action.payload.id)
        if (index !== -1) state.sessions[index] = action.payload
      })
      .addCase(completeSession.fulfilled, (state, action) => {
        const index = state.sessions.findIndex(s => s.id === action.payload.id)
        if (index !== -1) state.sessions[index] = action.payload
      })
  },
})

export const { setCurrentSession, clearError } = sessionSlice.actions
export default sessionSlice.reducer
