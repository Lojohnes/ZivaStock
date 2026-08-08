import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

export interface DashboardSession {
  id: number
  name: string
  status: string
  location: string
  counted_sections: number
  active_users: number
  created_at: string
}

export interface DashboardSummary {
  total_sessions: number
  active_sessions: number
  completed_sessions: number
  total_products: number
  total_counts: number
  total_users: number
  pending_duplicates: number
  total_sections: number
  counted_sections: number
  section_completion_percentage: number
  recent_counts_24h: number
}

export interface DashboardState {
  summary: DashboardSummary | null
  sessions: DashboardSession[]
  loading: boolean
  error: string | null
}

const initialState: DashboardState = {
  summary: null,
  sessions: [],
  loading: false,
  error: null,
}

export const fetchDashboardStats = createAsyncThunk(
  'dashboard/fetchDashboardStats',
  async () => {
    const response = await api.get('/reports/dashboard')
    return response.data
  }
)

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardStats.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchDashboardStats.fulfilled, (state, action) => {
        state.loading = false
        state.summary = action.payload.summary
        state.sessions = action.payload.sessions
      })
      .addCase(fetchDashboardStats.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch dashboard stats'
      })
  },
})

export const { clearError } = dashboardSlice.actions
export default dashboardSlice.reducer
