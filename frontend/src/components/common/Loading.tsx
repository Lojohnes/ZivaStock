import React from 'react'
import { Box, CircularProgress, Typography } from '@mui/material'

interface LoadingProps {
  message?: string
}

export const Loading: React.FC<LoadingProps> = ({ message = 'Loading...' }) => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      minHeight="200px"
    >
      <CircularProgress />
      <Typography variant="body2" sx={{ mt: 2 }} color="text.secondary">
        {message}
      </Typography>
    </Box>
  )
}
