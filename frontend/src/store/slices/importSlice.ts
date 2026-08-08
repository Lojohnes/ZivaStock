import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

interface ImportBatch {
  id: number
  filename: string
  source: string
  status: string
  total_records: number
  success_count: number
  error_count: number
  uploaded_by: number
  created_at: string
  detected_columns?: string[]
}

interface ImportState {
  batches: ImportBatch[]
  currentBatch: ImportBatch | null
  uploading: boolean
  processing: boolean
  error: string | null
  successMessage: string | null
}

const initialState: ImportState = {
  batches: [],
  currentBatch: null,
  uploading: false,
  processing: false,
  error: null,
  successMessage: null,
}

export const uploadImportFile = createAsyncThunk(
  'imports/uploadFile',
  async ({ file, source }: { file: File; source: string }, { rejectWithValue }) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await api.post(`/imports/upload?source=${encodeURIComponent(source)}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return response.data
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.detail || 'Upload failed')
    }
  }
)

export const processImportBatch = createAsyncThunk(
  'imports/processBatch',
  async (
    { batchId, fieldMapping }: { batchId: number; fieldMapping: Record<string, string> },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.post(`/imports/process/${batchId}`, { field_mapping: fieldMapping })
      return response.data
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.detail || 'Processing failed')
    }
  }
)

const importSlice = createSlice({
  name: 'imports',
  initialState,
  reducers: {
    clearMessages: (state) => {
      state.error = null
      state.successMessage = null
    },
    clearBatch: (state) => {
      state.currentBatch = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(uploadImportFile.pending, (state) => {
        state.uploading = true
        state.error = null
        state.successMessage = null
        state.currentBatch = null
      })
      .addCase(uploadImportFile.fulfilled, (state, action) => {
        state.uploading = false
        state.currentBatch = action.payload
        state.successMessage = `File uploaded successfully. ${action.payload.total_records} records detected.`
      })
      .addCase(uploadImportFile.rejected, (state, action) => {
        state.uploading = false
        state.error = action.payload as string
      })
      .addCase(processImportBatch.pending, (state) => {
        state.processing = true
        state.error = null
        state.successMessage = null
      })
      .addCase(processImportBatch.fulfilled, (state, action) => {
        state.processing = false
        state.successMessage = `Import complete. ${action.payload.success_count ?? 0} records imported, ${action.payload.error_count ?? 0} errors.`
      })
      .addCase(processImportBatch.rejected, (state, action) => {
        state.processing = false
        state.error = action.payload as string
      })
  },
})

export const { clearMessages, clearBatch } = importSlice.actions
export default importSlice.reducer
