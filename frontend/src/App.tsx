import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { Dashboard } from './pages/Dashboard'
import { Stocktake } from './pages/Stocktake'
import { Products } from './pages/Products'
import { Reports } from './pages/Reports'
import { Users } from './pages/Users'
import { Roles } from './pages/Roles'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Import } from './pages/Import'
import { Profile } from './pages/Profile'
import { Settings } from './pages/Settings'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="stocktake" element={<Stocktake />} />
        <Route path="products" element={<Products />} />
        <Route path="import" element={<Import />} />
        <Route path="reports" element={<Reports />} />
        <Route path="users" element={<Users />} />
        <Route path="roles" element={<Roles />} />
        <Route path="profile" element={<Profile />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}

export default App
