import React, { useEffect, useState } from 'react'
import {
  Box, Typography, Button, Dialog, DialogTitle, DialogContent,
  DialogActions, Alert, FormControl, InputLabel, Select, MenuItem,
  Checkbox, List, ListItem, ListItemText, Chip,
} from '@mui/material'
import { Security } from '@mui/icons-material'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import { Loading } from '../components/common/Loading'
import { ErrorAlert } from '../components/common/ErrorAlert'
import api from '../services/api'
import { fetchUsers } from '../store/slices/userSlice'

interface Permission {
  id: number
  name: string
  description: string | null
}

interface Role {
  id: number
  name: string
  description: string | null
  permissions: Permission[]
}

const roleLabels: Record<number, string> = {
  1: 'Super Admin',
  2: 'Stocktake Manager',
  3: 'Supervisor',
  4: 'Counter',
  5: 'Auditor',
}

export const Roles: React.FC = () => {
  const dispatch = useAppDispatch()
  const { users, loading: usersLoading, error: usersError } = useAppSelector((state) => state.users)
  const [roles, setRoles] = useState<Role[]>([])
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [open, setOpen] = useState(false)
  const [selectedRoleId, setSelectedRoleId] = useState<number>(1)
  const [selectedPerms, setSelectedPerms] = useState<number[]>([])
  const [saving, setSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState('')

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const [rolesRes, permsRes] = await Promise.all([
        api.get('/roles'),
        api.get('/roles/permissions/all'),
      ])
      setRoles(rolesRes.data)
      setPermissions(permsRes.data)
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to load roles/permissions')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    dispatch(fetchUsers({ page: 1, limit: 100 }))
  }, [dispatch])

  const handleOpen = (role: Role) => {
    setSelectedRoleId(role.id)
    setSelectedPerms(role.permissions.map((p) => p.id))
    setSaveMessage('')
    setOpen(true)
  }

  const togglePermission = (permId: number) => {
    setSelectedPerms((prev) =>
      prev.includes(permId) ? prev.filter((id) => id !== permId) : [...prev, permId]
    )
  }

  const handleSave = async () => {
    setSaving(true)
    setSaveMessage('')
    try {
      await api.put(`/roles/${selectedRoleId}/permissions`, { permission_ids: selectedPerms })
      setSaveMessage('Permissions updated successfully')
      await fetchData()
    } catch (e: any) {
      setSaveMessage(e.response?.data?.detail || 'Failed to update permissions')
    } finally {
      setSaving(false)
    }
  }

  if (loading && roles.length === 0) {
    return <Loading message="Loading roles..." />
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Roles & Permissions</Typography>
      </Box>

      {error && <Box mb={2}><ErrorAlert title="Load Error" message={error} /></Box>}
      {usersError && <Box mb={2}><ErrorAlert title="Users Error" message={usersError} /></Box>}

      <Box display="flex" flexDirection="column" gap={3}>
        <Box>
          <Typography variant="h6" gutterBottom>Roles</Typography>
          {roles.map((role) => (
            <Box key={role.id} mb={2} p={2} border="1px solid #e0e0e0" borderRadius={2}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography fontWeight={600}>{roleLabels[role.id] || role.name}</Typography>
                <Button variant="outlined" size="small" startIcon={<Security />} onClick={() => handleOpen(role)}>
                  Edit Permissions
                </Button>
              </Box>
              <Box display="flex" flexWrap="wrap" gap={0.5}>
                {role.permissions.map((p) => (
                  <Chip key={p.id} label={p.name} size="small" />
                ))}
              </Box>
            </Box>
          ))}
        </Box>

        <Box>
          <Typography variant="h6" gutterBottom>Users by Role</Typography>
          {usersLoading ? <Loading message="Loading users..." /> : (
            <Box display="flex" flexDirection="column" gap={1}>
              {roles.map((role) => (
                <Box key={role.id}>
                  <Typography fontWeight={600}>{roleLabels[role.id] || role.name}</Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5}>
                    {users.filter((u: any) => u.role_id === role.id).map((u: any) => (
                      <Chip key={u.id} label={`${u.first_name} ${u.last_name} (${u.email})`} size="small" />
                    ))}
                  </Box>
                </Box>
              ))}
            </Box>
          )}
        </Box>
      </Box>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Role Permissions</DialogTitle>
        <DialogContent>
          {saveMessage && <Alert severity={saveMessage.includes('success') ? 'success' : 'error'} sx={{ mb: 2 }}>{saveMessage}</Alert>}
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Role</InputLabel>
            <Select value={selectedRoleId} label="Role" onChange={(e) => setSelectedRoleId(Number(e.target.value))}>
              {roles.map((r) => (
                <MenuItem key={r.id} value={r.id}>{roleLabels[r.id] || r.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <Typography variant="subtitle2" gutterBottom>Permissions</Typography>
          <List dense>
            {permissions.map((perm) => (
              <ListItem key={perm.id} dense button onClick={() => togglePermission(perm.id)}>
                <Checkbox checked={selectedPerms.includes(perm.id)} />
                <ListItemText primary={perm.name} secondary={perm.description || ''} />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save Permissions'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
