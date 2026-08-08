import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role_id: number
  is_active: boolean
  last_login: string | null
  created_at: string
  updated_at: string
}

export interface UserState {
  users: User[]
  loading: boolean
  error: string | null
  total: number
  page: number
  limit: number
}

const initialState: UserState = {
  users: [],
  loading: false,
  error: null,
  total: 0,
  page: 1,
  limit: 20,
}

export const fetchUsers = createAsyncThunk(
  'users/fetchUsers',
  async (params: { page?: number; limit?: number; search?: string }) => {
    const response = await api.get('/users', { params })
    return response.data
  }
)

export const createUser = createAsyncThunk(
  'users/createUser',
  async (user: { email: string; first_name: string; last_name: string; password: string; role_id: number }) => {
    const response = await api.post('/users', user)
    return response.data
  }
)

const userSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false
        state.users = action.payload.items
        state.total = action.payload.total
        state.page = action.payload.page
        state.limit = action.payload.limit
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch users'
      })
      .addCase(createUser.fulfilled, (state, action) => {
        state.users.unshift(action.payload)
        state.total += 1
      })
  },
})

export const { clearError } = userSlice.actions
export default userSlice.reducer
