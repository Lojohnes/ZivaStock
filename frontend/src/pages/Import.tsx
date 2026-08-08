import React, { useRef, useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Divider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@mui/material'
import { CloudUpload, PlayArrow, CheckCircle } from '@mui/icons-material'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import {
  uploadImportFile,
  processImportBatch,
  clearMessages,
  clearBatch,
} from '../store/slices/importSlice'

const SOURCES = [
  { value: 'sage_evolution', label: 'Sage Evolution' },
  { value: 'csv', label: 'CSV File' },
  { value: 'excel', label: 'Excel File' },
  { value: 'manual', label: 'Manual Entry' },
]

const FIELD_MAPPING_DEFAULTS: Record<string, string> = {
  barcode: 'Item Code',
  description: 'Item Description',
  product_code: 'Item Code',
  unit_of_measure: 'Unit',
  system_quantity: 'Qty On Hand',
  unit_cost: 'Unit Cost',
}

const steps = ['Select File', 'Review & Map Fields', 'Import']

export const Import: React.FC = () => {
  const dispatch = useAppDispatch()
  const { currentBatch, uploading, processing, error, successMessage } = useAppSelector(
    (state) => state.imports
  )

  const [activeStep, setActiveStep] = useState(0)
  const [source, setSource] = useState('csv')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [fieldMapping, setFieldMapping] = useState<Record<string, string>>(FIELD_MAPPING_DEFAULTS)
  const [processResult, setProcessResult] = useState<{ success_count: number; error_count: number; errors: string[] } | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return
    const result = await dispatch(uploadImportFile({ file: selectedFile, source }))
    if (uploadImportFile.fulfilled.match(result)) {
      setActiveStep(1)
    }
  }

  const handleProcess = async () => {
    if (!currentBatch) return
    const result = await dispatch(
      processImportBatch({ batchId: currentBatch.id, fieldMapping })
    )
    if (processImportBatch.fulfilled.match(result)) {
      setProcessResult(result.payload as any)
      setActiveStep(2)
    }
  }

  const handleReset = () => {
    setActiveStep(0)
    setSelectedFile(null)
    setSource('csv')
    setFieldMapping(FIELD_MAPPING_DEFAULTS)
    setProcessResult(null)
    dispatch(clearMessages())
    dispatch(clearBatch())
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Import Inventory
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => dispatch(clearMessages())}>
          {error}
        </Alert>
      )}
      {successMessage && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => dispatch(clearMessages())}>
          {successMessage}
        </Alert>
      )}

      {/* Step 0: Select File */}
      {activeStep === 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Step 1: Choose File & Source
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <Box display="flex" gap={3} flexWrap="wrap" alignItems="flex-start">
            <FormControl sx={{ minWidth: 220 }}>
              <InputLabel>Import Source</InputLabel>
              <Select
                value={source}
                label="Import Source"
                onChange={(e) => setSource(e.target.value as string)}
              >
                {SOURCES.map((s) => (
                  <MenuItem key={s.value} value={s.value}>
                    {s.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Box>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.xlsx,.xls"
                style={{ display: 'none' }}
                onChange={handleFileChange}
              />
              <Button
                variant="outlined"
                startIcon={<CloudUpload />}
                onClick={() => fileInputRef.current?.click()}
              >
                {selectedFile ? selectedFile.name : 'Choose File (.csv, .xlsx)'}
              </Button>
              {selectedFile && (
                <Chip
                  label={`${(selectedFile.size / 1024).toFixed(1)} KB`}
                  size="small"
                  sx={{ ml: 1 }}
                />
              )}
            </Box>
          </Box>

          <Box mt={3}>
            <Button
              variant="contained"
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              startIcon={uploading ? <CircularProgress size={18} /> : <CloudUpload />}
            >
              {uploading ? 'Uploading...' : 'Upload File'}
            </Button>
          </Box>
        </Paper>
      )}

      {/* Step 1: Field Mapping */}
      {activeStep === 1 && currentBatch && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Step 2: Review & Map Fields
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <Box mb={3}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Batch ID: <strong>{currentBatch.id}</strong> &nbsp;|&nbsp; File:{' '}
              <strong>{currentBatch.filename}</strong> &nbsp;|&nbsp; Records detected:{' '}
              <strong>{currentBatch.total_records}</strong>
            </Typography>
          </Box>

          {currentBatch.detected_columns && currentBatch.detected_columns.length > 0 && (
            <Box mb={2} p={1.5} sx={{ bgcolor: '#f0f4ff', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary" fontWeight={600}>
                Detected columns in your file:&nbsp;
              </Typography>
              {currentBatch.detected_columns.map((col: string) => (
                <Chip key={col} label={col} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
              ))}
            </Box>
          )}

          <Typography variant="subtitle2" gutterBottom>
            Field Mapping — enter the exact column name from your file for each system field
          </Typography>
          <Table size="small" sx={{ mb: 3, maxWidth: 560 }}>
            <TableHead>
              <TableRow>
                <TableCell>System Field</TableCell>
                <TableCell>Column name in your file</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Object.entries(fieldMapping).map(([field, mapped]) => (
                <TableRow key={field}>
                  <TableCell sx={{ fontWeight: 500 }}>{field}</TableCell>
                  <TableCell>
                    <input
                      value={mapped}
                      onChange={(e) =>
                        setFieldMapping((prev) => ({ ...prev, [field]: e.target.value }))
                      }
                      style={{
                        border: '1px solid #ccc',
                        borderRadius: 4,
                        padding: '4px 8px',
                        width: '100%',
                      }}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <Box display="flex" gap={2}>
            <Button variant="outlined" onClick={handleReset}>
              Start Over
            </Button>
            <Button
              variant="contained"
              onClick={handleProcess}
              disabled={processing}
              startIcon={processing ? <CircularProgress size={18} /> : <PlayArrow />}
            >
              {processing ? 'Processing...' : 'Run Import'}
            </Button>
          </Box>
        </Paper>
      )}

      {/* Step 2: Done */}
      {activeStep === 2 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Import Complete
          </Typography>
          {processResult && (
            <Box mb={2}>
              <Typography variant="h6" color="success.main">
                {processResult.success_count} products imported successfully
              </Typography>
              {processResult.error_count > 0 && (
                <Typography variant="body2" color="error">
                  {processResult.error_count} rows had errors
                </Typography>
              )}
              {processResult.errors && processResult.errors.length > 0 && (
                <Box mt={1} textAlign="left" sx={{ maxHeight: 150, overflowY: 'auto', bgcolor: '#fff3f3', p: 1, borderRadius: 1 }}>
                  {processResult.errors.slice(0, 10).map((e, i) => (
                    <Typography key={i} variant="caption" display="block" color="error">{e}</Typography>
                  ))}
                  {processResult.errors.length > 10 && (
                    <Typography variant="caption" color="text.secondary">...and {processResult.errors.length - 10} more</Typography>
                  )}
                </Box>
              )}
            </Box>
          )}
          <Box mt={3} display="flex" gap={2} justifyContent="center">
            <Button variant="outlined" onClick={handleReset}>
              Import Another File
            </Button>
            <Button variant="contained" href="/products">
              View Products
            </Button>
          </Box>
        </Paper>
      )}
    </Box>
  )
}
