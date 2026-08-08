import React, { useState } from 'react'
import {
  Box, Container, TextField, Button, Typography, Paper, Alert, Grid, Link as MuiLink
} from '@mui/material'
import { useNavigate, Link } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import { register } from '../store/slices/authSlice'

export const Register: React.FC = () => {
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirm_password: '',
  })
  const [formError, setFormError] = useState('')
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { loading, error } = useAppSelector((state) => state.auth)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError('')

    if (form.password !== form.confirm_password) {
      setFormError('Passwords do not match.')
      return
    }
    if (form.password.length < 8) {
      setFormError('Password must be at least 8 characters.')
      return
    }

    const result = await dispatch(register({
      email: form.email,
      password: form.password,
      first_name: form.first_name,
      last_name: form.last_name,
    }))

    if (register.fulfilled.match(result)) {
      navigate('/dashboard')
    }
  }

  return (
    <Container component="main" maxWidth="xs">
      <Box sx={{ marginTop: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography component="h1" variant="h5" align="center" gutterBottom>
            ZivaStock
          </Typography>
          <Typography variant="body2" align="center" color="text.secondary" sx={{ mb: 3 }}>
            Create your account
          </Typography>

          {(formError || error) && (
            <Alert severity="error" sx={{ mb: 2 }}>{formError || error}</Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  required fullWidth label="First Name" name="first_name"
                  value={form.first_name} onChange={handleChange} autoFocus
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  required fullWidth label="Last Name" name="last_name"
                  value={form.last_name} onChange={handleChange}
                />
              </Grid>
            </Grid>
            <TextField
              margin="normal" required fullWidth label="Email Address"
              name="email" type="email" autoComplete="email"
              value={form.email} onChange={handleChange}
            />
            <TextField
              margin="normal" required fullWidth label="Password"
              name="password" type="password"
              value={form.password} onChange={handleChange}
            />
            <TextField
              margin="normal" required fullWidth label="Confirm Password"
              name="confirm_password" type="password"
              value={form.confirm_password} onChange={handleChange}
            />
            <Button
              type="submit" fullWidth variant="contained"
              sx={{ mt: 3, mb: 2 }} disabled={loading}
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </Button>
            <Box textAlign="center">
              <MuiLink component={Link} to="/login" variant="body2">
                Already have an account? Sign in
              </MuiLink>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  )
}
