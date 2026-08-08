import React from 'react'
import { Avatar, Menu, MenuItem, IconButton } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useAppSelector } from '../../hooks/redux'

export const Header: React.FC = () => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null)
  const navigate = useNavigate()
  const user = useAppSelector((state) => state.auth.user)

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  return (
    <>
      <IconButton
        size="large"
        aria-label="account of current user"
        aria-controls="menu-appbar"
        aria-haspopup="true"
        onClick={handleMenu}
        color="inherit"
      >
        <Avatar src={user?.profile_picture || undefined} sx={{ width: 32, height: 32 }}>
          {user?.first_name?.charAt(0) || 'U'}
        </Avatar>
      </IconButton>
      <Menu
        id="menu-appbar"
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <MenuItem onClick={() => { handleClose(); navigate('/profile') }}>Profile</MenuItem>
        <MenuItem onClick={() => { handleClose(); navigate('/settings') }}>Settings</MenuItem>
      </Menu>
    </>
  )
}
