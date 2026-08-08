import React, { useEffect, useState } from 'react'
import {
  Box, Typography, Button, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, MenuItem, Select, InputLabel,
  FormControl, Alert,
} from '@mui/material'
import { Add, Edit, LockReset } from '@mui/icons-material'
import { DataGrid, GridColDef, GridActionsCellItem } from '@mui/x-data-grid'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import { fetchUsers } from '../store/slices/userSlice'
import { Loading } from '../components/common/Loading'
import { ErrorAlert } from '../components/common/ErrorAlert'
import api from '../services/api'

const roleLabels: Record<number, string> = {
  1: 'Super Admin',
  2: 'Stocktake Manager',
  3: 'Supervisor',
  4: 'Counter',
  5: 'Auditor',
}

const EMPTY_FORM = { email: '', first_name: '', last_name: '', password: '', role_id: 4 }

export const Users: React.FC = () => {
  const dispatch = useAppDispatch()
  const { users, loading, error, total, page, limit } = useAppSelector((state) => state.users)
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')

  const [resetOpen, setResetOpen] = useState(false)
  const [resetUserId, setResetUserId] = useState<number | null>(null)
  const [newPassword, setNewPassword] = useState('')
  const [resetSaving, setResetSaving] = useState(false)
  const [resetMessage, setResetMessage] = useState('')

  const [roleOpen, setRoleOpen] = useState(false)
  const [roleUserId, setRoleUserId] = useState<number | null>(null)
  const [selectedRoleId, setSelectedRoleId] = useState<number>(4)
  const [roleSaving, setRoleSaving] = useState(false)
  const [roleMessage, setRoleMessage] = useState('')

  const openResetPassword = (userId: number) => {
    setResetUserId(userId)
    setNewPassword('')
    setResetMessage('')
    setResetOpen(true)
  }

  const openChangeRole = (userId: number, roleId: number) => {
    setRoleUserId(userId)
    setSelectedRoleId(roleId)
    setRoleMessage('')
    setRoleOpen(true)
  }

  const handleResetPassword = async () => {
    if (!resetUserId || !newPassword || newPassword.length < 8) {
      setResetMessage('Password must be at least 8 characters')
      return
    }
    setResetSaving(true)
    try {
      await api.post(`/users/${resetUserId}/reset-password`, { new_password: newPassword })
      setResetMessage('Password reset successfully')
      setNewPassword('')
    } catch (e: any) {
      setResetMessage(e.response?.data?.detail || 'Failed to reset password')
    } finally {
      setResetSaving(false)
    }
  }

  const handleChangeRole = async () => {
    if (!roleUserId) return
    setRoleSaving(true)
    try {
      await api.put(`/users/${roleUserId}`, { role_id: selectedRoleId })
      setRoleMessage('Role updated successfully')
      dispatch(fetchUsers({ page, limit }))
    } catch (e: any) {
      setRoleMessage(e.response?.data?.detail || 'Failed to update role')
    } finally {
      setRoleSaving(false)
    }
  }

  const columns: GridColDef[] = [
    { field: 'email', headerName: 'Email', flex: 1, minWidth: 200 },
    { field: 'first_name', headerName: 'First Name', width: 150 },
    { field: 'last_name', headerName: 'Last Name', width: 150 },
    {
      field: 'role_id',
      headerName: 'Role',
      width: 160,
      valueGetter: (params: { value: unknown }) => roleLabels[params.value as number] || `Role ${params.value}`,
    },
    { field: 'is_active', headerName: 'Active', width: 100, type: 'boolean' },
    {
      field: 'last_login',
      headerName: 'Last Login',
      width: 180,
      valueGetter: (params: { value: unknown }) => (params.value ? new Date(params.value as string).toLocaleString() : 'Never'),
    },
    {
      field: 'actions',
      type: 'actions',
      headerName: 'Actions',
      width: 120,
      getActions: (params: any) => [
        <GridActionsCellItem
          icon={<LockReset />}
          label="Reset Password"
          onClick={() => openResetPassword(params.id as number)}
          key="reset"
        />,
        <GridActionsCellItem
          icon={<Edit />}
          label="Change Role"
          onClick={() => openChangeRole(params.id as number, params.row.role_id as number)}
          key="role"
        />,
      ],
    },
  ]

  useEffect(() => {
    dispatch(fetchUsers({ page: 1, limit: 20 }))
  }, [dispatch])

  const handleSave = async () => {
    if (!form.email || !form.first_name || !form.last_name || !form.password) {
      setFormError('All fields are required')
      return
    }
    setSaving(true)
    setFormError('')
    try {
      await api.post('/users', form)
      setOpen(false)
      setForm(EMPTY_FORM)
      dispatch(fetchUsers({ page: 1, limit: 20 }))
    } catch (e: any) {
      setFormError(e.response?.data?.detail || 'Failed to create user')
    } finally {
      setSaving(false)
    }
  }

  if (loading && users.length === 0) {
    return <Loading message="Loading users..." />
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Users</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => { setOpen(true); setFormError('') }}>
          Add User
        </Button>
      </Box>

      {error && <Box mb={2}><ErrorAlert title="Load Error" message={error} /></Box>}

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New User</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          {formError && <Alert severity="error">{formError}</Alert>}
          <TextField label="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} fullWidth />
          <TextField label="First Name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} fullWidth />
          <TextField label="Last Name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} fullWidth />
          <TextField label="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} fullWidth />
          <FormControl fullWidth>
            <InputLabel>Role</InputLabel>
            <Select value={form.role_id} label="Role" onChange={(e) => setForm({ ...form, role_id: Number(e.target.value) })}>
              {Object.entries(roleLabels).map(([id, label]) => (
                <MenuItem key={id} value={Number(id)}>{label}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave} disabled={saving}>
            {saving ? 'Creating...' : 'Create User'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={resetOpen} onClose={() => setResetOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Reset User Password</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          {resetMessage && <Alert severity={resetMessage.includes('success') ? 'success' : 'error'}>{resetMessage}</Alert>}
          <TextField
            label="New Password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            fullWidth
            helperText="At least 8 characters"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleResetPassword} disabled={resetSaving}>
            {resetSaving ? 'Resetting...' : 'Reset Password'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={roleOpen} onClose={() => setRoleOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Change User Role</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          {roleMessage && <Alert severity={roleMessage.includes('success') ? 'success' : 'error'}>{roleMessage}</Alert>}
          <FormControl fullWidth>
            <InputLabel>Role</InputLabel>
            <Select value={selectedRoleId} label="Role" onChange={(e) => setSelectedRoleId(Number(e.target.value))}>
              {Object.entries(roleLabels).map(([id, label]) => (
                <MenuItem key={id} value={Number(id)}>{label}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRoleOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleChangeRole} disabled={roleSaving}>
            {roleSaving ? 'Saving...' : 'Change Role'}
          </Button>
        </DialogActions>
      </Dialog>

      <DataGrid
        rows={users}
        columns={columns}
        rowCount={total}
        loading={loading}
        pagination
        pageSizeOptions={[10, 20, 50]}
        initialState={{ pagination: { paginationModel: { page: page - 1, pageSize: limit } } }}
        onPaginationModelChange={(model) => dispatch(fetchUsers({ page: model.page + 1, limit: model.pageSize }))}
        disableRowSelectionOnClick
        autoHeight
        density="compact"
      />
    </Box>
  )
}
