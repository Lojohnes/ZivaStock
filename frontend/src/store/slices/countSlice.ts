import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

interface Count {
  id: number
  product_id: number
  section_id: number
  quantity: number
  user_id: number
  session_id: number
  counted_at: string
  synced_at: string | null
  is_synced: boolean
}

interface CountState {
  counts: Count[]
  loading: boolean
  error: string | null
  total: number
}

const initialState: CountState = {
  counts: [],
  loading: false,
  error: null,
  total: 0,
}

export const fetchCounts = createAsyncThunk(
  'counts/fetchCounts',
  async (params: { session_id?: number; section_id?: number; user_id?: number }) => {
    const response = await api.get('/counts', { params })
    return response.data
  }
)

export const createCount = createAsyncThunk(
  'counts/createCount',
  async (count: Omit<Count, 'id' | 'counted_at' | 'synced_at' | 'is_synced'>) => {
    const response = await api.post('/counts', count)
    return response.data
  }
)

const countSlice = createSlice({
  name: 'counts',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCounts.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchCounts.fulfilled, (state, action) => {
        state.loading = false
        state.counts = action.payload.items
        state.total = action.payload.total
      })
      .addCase(fetchCounts.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch counts'
      })
      .addCase(createCount.fulfilled, (state, action) => {
        state.counts.push(action.payload)
      })
  },
})

export const { clearError } = countSlice.actions
export default countSlice.reducer
