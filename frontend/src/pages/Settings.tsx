import { useState } from 'react'
import { Alert, Box, Button, FormControlLabel, Paper, Switch, Typography } from '@mui/material'
import { Save } from '@mui/icons-material'

export const Settings: React.FC = () => {
  const [notifications, setNotifications] = useState(localStorage.getItem('zivastock_notifications') !== 'false')
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    localStorage.setItem('zivastock_notifications', String(notifications))
    setSaved(true)
  }

  return (
    <Box maxWidth={720}>
      <Typography variant="h4" gutterBottom>Settings</Typography>
      <Paper sx={{ p: 3 }}>
        {saved && <Alert severity="success" sx={{ mb: 2 }}>Settings saved successfully</Alert>}
        <Typography variant="h6" gutterBottom>Notifications</Typography>
        <FormControlLabel
          control={<Switch checked={notifications} onChange={(e) => { setNotifications(e.target.checked); setSaved(false) }} />}
          label="Enable stocktake and synchronization notifications"
        />
        <Box mt={3}>
          <Button variant="contained" startIcon={<Save />} onClick={handleSave}>Save settings</Button>
        </Box>
      </Paper>
    </Box>
  )
}
