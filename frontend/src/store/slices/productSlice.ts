import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

interface Product {
  id: number
  barcode: string
  product_code: string | null
  description: string
  unit_of_measure: string
  system_quantity: number
  unit_cost: number
  created_at: string
  updated_at: string
}

interface ProductState {
  products: Product[]
  loading: boolean
  error: string | null
  total: number
  page: number
  limit: number
}

const initialState: ProductState = {
  products: [],
  loading: false,
  error: null,
  total: 0,
  page: 1,
  limit: 500,
}

export const fetchProducts = createAsyncThunk(
  'products/fetchProducts',
  async (params: { page?: number; limit?: number; search?: string }) => {
    const response = await api.get('/products', { params })
    return response.data
  }
)

export const createProduct = createAsyncThunk(
  'products/createProduct',
  async (product: Omit<Product, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await api.post('/products', product)
    return response.data
  }
)

const productSlice = createSlice({
  name: 'products',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false
        state.products = action.payload.items
        state.total = action.payload.total
        state.page = action.payload.page
        state.limit = action.payload.limit
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch products'
      })
      .addCase(createProduct.fulfilled, (state, action) => {
        state.products.push(action.payload)
      })
  },
})

export const { clearError } = productSlice.actions
export default productSlice.reducer
