import { useEffect, useRef, useState } from 'react'
import { Alert, Avatar, Box, Button, CircularProgress, Paper, Stack, TextField, Typography } from '@mui/material'
import { PhotoCamera, Save } from '@mui/icons-material'
import api from '../services/api'
import { useAppDispatch } from '../hooks/redux'
import { setUser } from '../store/slices/authSlice'

interface ProfileData {
  id: number
  email: string
  first_name: string
  last_name: string
  phone_number: string | null
  profile_picture: string | null
}

export const Profile: React.FC = () => {
  const dispatch = useAppDispatch()
  const [profile, setProfile] = useState<ProfileData | null>(null)
  const [form, setForm] = useState({ first_name: '', last_name: '', phone_number: '' })
  const [picture, setPicture] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    api.get('/auth/me').then((response) => {
      const user = response.data as ProfileData
      setProfile(user)
      setForm({ first_name: user.first_name, last_name: user.last_name, phone_number: user.phone_number || '' })
      setPicture(user.profile_picture)
    }).catch((error) => {
      setMessage(error.response?.data?.detail || 'Unable to load your profile')
    }).finally(() => setLoading(false))
  }, [])

  const handlePicture = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    if (!file.type.startsWith('image/')) {
      setMessage('Please choose an image file')
      return
    }
    if (file.size > 2 * 1024 * 1024) {
      setMessage('Profile pictures must be smaller than 2 MB')
      return
    }
    const reader = new FileReader()
    reader.onload = () => setPicture(String(reader.result))
    reader.readAsDataURL(file)
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage('')
    try {
      const response = await api.put('/auth/me', { ...form, profile_picture: picture })
      setProfile(response.data)
      dispatch(setUser(response.data))
      setMessage('Profile updated successfully')
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Unable to update your profile')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <CircularProgress />

  return (
    <Box maxWidth={720}>
      <Typography variant="h4" gutterBottom>My Profile</Typography>
      <Paper sx={{ p: 3 }}>
        {message && <Alert severity={message.includes('successfully') ? 'success' : 'error'} sx={{ mb: 2 }}>{message}</Alert>}
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} alignItems={{ xs: 'center', sm: 'flex-start' }}>
          <Stack alignItems="center" spacing={1}>
            <Avatar src={picture || undefined} sx={{ width: 112, height: 112, bgcolor: 'primary.main', fontSize: 42 }}>
              {form.first_name.charAt(0)}
            </Avatar>
            <input ref={fileRef} hidden type="file" accept="image/*" onChange={handlePicture} />
            <Button size="small" startIcon={<PhotoCamera />} onClick={() => fileRef.current?.click()}>Change picture</Button>
            {picture && <Button size="small" color="inherit" onClick={() => setPicture(null)}>Remove picture</Button>}
          </Stack>
          <Stack spacing={2} flex={1} width="100%">
            <TextField label="Email" value={profile?.email || ''} disabled fullWidth />
            <TextField label="First name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} fullWidth />
            <TextField label="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} fullWidth />
            <TextField label="Phone number" value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} fullWidth />
            <Button variant="contained" startIcon={<Save />} onClick={handleSave} disabled={saving}>
              {saving ? 'Saving...' : 'Save profile'}
            </Button>
          </Stack>
        </Stack>
      </Paper>
    </Box>
  )
}
