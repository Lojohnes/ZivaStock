import React, { useEffect, useState } from 'react'
import { Box, Typography, Button, TextField } from '@mui/material'
import { Add, Search } from '@mui/icons-material'
import { DataGrid, GridColDef } from '@mui/x-data-grid'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import { fetchProducts } from '../store/slices/productSlice'
import { Loading } from '../components/common/Loading'
import { ErrorAlert } from '../components/common/ErrorAlert'

const columns: GridColDef[] = [
  { field: 'barcode', headerName: 'Barcode', width: 150 },
  { field: 'product_code', headerName: 'Product Code', width: 130 },
  { field: 'description', headerName: 'Description', flex: 1, minWidth: 250 },
  { field: 'unit_of_measure', headerName: 'UOM', width: 80 },
  { field: 'system_quantity', headerName: 'System Qty', width: 120, type: 'number' },
  { field: 'unit_cost', headerName: 'Unit Cost', width: 120, type: 'number' },
  { field: 'is_active', headerName: 'Active', width: 100, type: 'boolean' },
]

export const Products: React.FC = () => {
  const dispatch = useAppDispatch()
  const { products, loading, error } = useAppSelector((state) => state.products)
  const [search, setSearch] = useState('')
  const [, setPageSize] = useState(100)

  useEffect(() => {
    dispatch(fetchProducts({ page: 1, limit: 5000, search }))
  }, [dispatch, search])

  if (loading && products.length === 0) {
    return <Loading message="Loading products..." />
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Products</Typography>
        <Button variant="contained" startIcon={<Add />}>
          Add Product
        </Button>
      </Box>

      {error && <Box mb={2}><ErrorAlert title="Load Error" message={error} /></Box>}

      <Box mb={2}>
        <TextField
          placeholder="Search products..."
          size="small"
          value={search}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
          InputProps={{ startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} /> }}
          sx={{ width: 300 }}
        />
      </Box>

      <DataGrid
        rows={products}
        columns={columns}
        loading={loading}
        pagination
        pageSizeOptions={[25, 50, 100, 250, 500]}
        initialState={{ pagination: { paginationModel: { pageSize: 100 } } }}
        onPaginationModelChange={(model) => setPageSize(model.pageSize)}
        disableRowSelectionOnClick
        autoHeight
        density="compact"
      />
    </Box>
  )
}
