import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import productReducer from './slices/productSlice'
import countReducer from './slices/countSlice'
import sessionReducer from './slices/sessionSlice'
import dashboardReducer from './slices/dashboardSlice'
import userReducer from './slices/userSlice'
import importReducer from './slices/importSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    products: productReducer,
    counts: countReducer,
    sessions: sessionReducer,
    dashboard: dashboardReducer,
    users: userReducer,
    imports: importReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
