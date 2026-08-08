import React, { useEffect } from 'react'
import {
  Box,
  Typography,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material'
import {
  Inventory,
  CheckCircle,
  People,
  Warning,
  TrendingUp,
  Assignment,
} from '@mui/icons-material'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import { fetchDashboardStats } from '../store/slices/dashboardSlice'
import { KPICard } from '../components/dashboard/KPICard'
import { Loading } from '../components/common/Loading'
import { ErrorAlert } from '../components/common/ErrorAlert'

const statusColor: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'error'> = {
  not_started: 'default',
  in_progress: 'primary',
  paused: 'warning',
  completed: 'success',
  archived: 'default',
}

export const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch()
  const { summary, sessions, loading, error } = useAppSelector((state) => state.dashboard)

  useEffect(() => {
    dispatch(fetchDashboardStats())
  }, [dispatch])

  if (loading) {
    return <Loading message="Loading dashboard..." />
  }

  if (error) {
    return <ErrorAlert title="Dashboard Error" message={error} onRetry={() => dispatch(fetchDashboardStats())} />
  }

  if (!summary) {
    return <ErrorAlert title="No Data" message="Dashboard statistics are unavailable." />
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <KPICard
            title="Total Sessions"
            value={summary.total_sessions}
            icon={<Assignment />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <KPICard
            title="Active Sessions"
            value={summary.active_sessions}
            subtitle="In progress"
            icon={<TrendingUp />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <KPICard
            title="Completed"
            value={summary.completed_sessions}
            icon={<CheckCircle />}
            color="#0288d1"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <KPICard
            title="Products"
            value={summary.total_products}
            icon={<Inventory />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <KPICard
            title="Total Counts"
            value={summary.total_counts}
            subtitle={`${summary.recent_counts_24h} in last 24h`}
            icon={<People />}
            color="#9c27b0"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <KPICard
            title="Pending Duplicates"
            value={summary.pending_duplicates}
            icon={<Warning />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Section Completion
            </Typography>
            <Typography variant="h3" color="primary">
              {summary.section_completion_percentage}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {summary.counted_sections} of {summary.total_sections} sections counted
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Active Users
            </Typography>
            <Typography variant="h3" color="primary">
              {summary.total_users}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Registered users in the system
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ mt: 3, p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Stocktake Sessions
        </Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Location</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Counts</TableCell>
                <TableCell align="right">Active Users</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sessions.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    No sessions found
                  </TableCell>
                </TableRow>
              )}
              {sessions.map((session) => (
                <TableRow key={session.id} hover>
                  <TableCell>{session.name}</TableCell>
                  <TableCell>{session.location}</TableCell>
                  <TableCell>
                    <Chip
                      label={session.status.replace('_', ' ')}
                      color={statusColor[session.status] || 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">{session.counted_sections}</TableCell>
                  <TableCell align="right">{session.active_users}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  )
}
