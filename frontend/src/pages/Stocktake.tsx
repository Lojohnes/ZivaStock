import React, { useEffect, useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert,
} from '@mui/material'
import { Add, PlayArrow, Pause, CheckCircle } from '@mui/icons-material'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import { fetchSessions, createSession, startSession, Session } from '../store/slices/sessionSlice'
import { Loading } from '../components/common/Loading'
import { ErrorAlert } from '../components/common/ErrorAlert'
import api from '../services/api'

const statusColor: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'error'> = {
  not_started: 'default',
  in_progress: 'primary',
  paused: 'warning',
  completed: 'success',
  archived: 'default',
}

const EMPTY_FORM = { name: '', description: '', location_id: 1 }

export const Stocktake: React.FC = () => {
  const dispatch = useAppDispatch()
  const { sessions, loading, error } = useAppSelector((state) => state.sessions)
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [locations, setLocations] = useState<{ id: number; name: string; type: string }[]>([])
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')
  const [locationOpen, setLocationOpen] = useState(false)
  const [locationForm, setLocationForm] = useState({ name: '', type: 'warehouse', address: '' })
  const [locationSaving, setLocationSaving] = useState(false)
  const [locationError, setLocationError] = useState('')

  useEffect(() => {
    dispatch(fetchSessions({}))
    api.get('/locations').then((r) => setLocations(r.data?.items || r.data || [])).catch(() => {})
  }, [dispatch])

  const handleStart = (id: number) => {
    dispatch(startSession(id))
  }

  const handleCreateLocation = async () => {
    if (!locationForm.name.trim()) {
      setLocationError('Warehouse or shop name is required')
      return
    }
    setLocationSaving(true)
    setLocationError('')
    try {
      const response = await api.post('/locations', {
        name: locationForm.name.trim(),
        type: locationForm.type,
        address: locationForm.address.trim() || null,
        parent_id: null,
      })
      const location = response.data
      setLocations((current) => [...current, location])
      setForm((current) => ({ ...current, location_id: location.id }))
      setLocationForm({ name: '', type: 'warehouse', address: '' })
      setLocationOpen(false)
    } catch (e: any) {
      setLocationError(e.response?.data?.detail || 'Failed to create location')
    } finally {
      setLocationSaving(false)
    }
  }

  const handleCreate = async () => {
    if (!form.name.trim()) {
      setFormError('Session name is required')
      return
    }
    setSaving(true)
    setFormError('')
    try {
      await dispatch(createSession({
        name: form.name,
        description: form.description || null,
        location_id: form.location_id,
        start_time: null,
        end_time: null,
        status: 'not_started',
      })).unwrap()
      setOpen(false)
      setForm(EMPTY_FORM)
      dispatch(fetchSessions({}))
    } catch (e: any) {
      setFormError(e?.message || 'Failed to create session')
    } finally {
      setSaving(false)
    }
  }

  if (loading && sessions.length === 0) {
    return <Loading message="Loading stocktake sessions..." />
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Stocktake Sessions</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => { setOpen(true); setFormError('') }}>
          New Session
        </Button>
      </Box>

      {error && <ErrorAlert title="Load Error" message={error} />}

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Stocktake Session</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          {formError && <Alert severity="error">{formError}</Alert>}
          <TextField
            label="Session Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            fullWidth
            required
          />
          <TextField
            label="Description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            fullWidth
            multiline
            rows={2}
          />
          <Box display="flex" gap={1} alignItems="center">
            <TextField
              select
              label="Warehouse / Shop"
              value={form.location_id}
              onChange={(e) => setForm({ ...form, location_id: Number(e.target.value) })}
              fullWidth
            >
              {locations.map((loc) => (
                <MenuItem key={loc.id} value={loc.id}>{loc.name} ({loc.type})</MenuItem>
              ))}
            </TextField>
            <Button variant="outlined" onClick={() => { setLocationError(''); setLocationOpen(true) }}>
              New location
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate} disabled={saving}>
            {saving ? 'Creating...' : 'Create Session'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={locationOpen} onClose={() => setLocationOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Warehouse or Shop</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          {locationError && <Alert severity="error">{locationError}</Alert>}
          <TextField
            label="Name"
            value={locationForm.name}
            onChange={(e) => setLocationForm({ ...locationForm, name: e.target.value })}
            placeholder="e.g. Harare Main Shop"
            required
            fullWidth
          />
          <TextField
            select
            label="Type"
            value={locationForm.type}
            onChange={(e) => setLocationForm({ ...locationForm, type: e.target.value })}
            fullWidth
          >
            <MenuItem value="warehouse">Warehouse</MenuItem>
            <MenuItem value="store">Shop / Store</MenuItem>
            <MenuItem value="zone">Zone</MenuItem>
            <MenuItem value="area">Area</MenuItem>
          </TextField>
          <TextField
            label="Address (optional)"
            value={locationForm.address}
            onChange={(e) => setLocationForm({ ...locationForm, address: e.target.value })}
            fullWidth
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLocationOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateLocation} disabled={locationSaving}>
            {locationSaving ? 'Creating...' : 'Create location'}
          </Button>
        </DialogActions>
      </Dialog>

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Start Time</TableCell>
              <TableCell>End Time</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sessions.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No stocktake sessions found
                </TableCell>
              </TableRow>
            )}
            {sessions.map((session: Session) => (
              <TableRow key={session.id} hover>
                <TableCell>{session.name}</TableCell>
                <TableCell>{session.description || '-'}</TableCell>
                <TableCell>
                  <Chip
                    label={session.status.replace('_', ' ')}
                    color={statusColor[session.status] || 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{session.start_time ? new Date(session.start_time).toLocaleString() : '-'}</TableCell>
                <TableCell>{session.end_time ? new Date(session.end_time).toLocaleString() : '-'}</TableCell>
                <TableCell align="right">
                  {session.status === 'not_started' && (
                    <Tooltip title="Start Session">
                      <IconButton color="primary" onClick={() => handleStart(session.id)}>
                        <PlayArrow />
                      </IconButton>
                    </Tooltip>
                  )}
                  {session.status === 'in_progress' && (
                    <Tooltip title="Pause">
                      <IconButton color="warning">
                        <Pause />
                      </IconButton>
                    </Tooltip>
                  )}
                  {session.status === 'in_progress' && (
                    <Tooltip title="Complete">
                      <IconButton color="success">
                        <CheckCircle />
                      </IconButton>
                    </Tooltip>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}
