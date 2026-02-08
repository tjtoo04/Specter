import { type WithAuthInfoProps, withAuthInfo } from '@propelauth/react'
import { useEffect, useState, useRef } from 'react'
import {
    Container,
    Box,
    Typography,
    Button,
    Card,
    CardContent,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    IconButton,
    Alert,
    CircularProgress,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Chip,
} from '@mui/material'
import {
    Upload,
    Download,
    Delete,
    CloudUpload,
    Description,
    Edit,
} from '@mui/icons-material'
import { api } from '../lib/api'
import type { Report } from '../types'


const ReportsPage = withAuthInfo((props: WithAuthInfoProps) => {
    const [reports, setReports] = useState<Report[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [success, setSuccess] = useState<string | null>(null)

    // Dialog states
    const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
    const [updateDialogOpen, setUpdateDialogOpen] = useState(false)
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)

    // Form states
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [updatingReportId, setUpdatingReportId] = useState<number | null>(null)
    const [updateFile, setUpdateFile] = useState<File | null>(null)
    const [deletingReport, setDeletingReport] = useState<Report | null>(null)

    // Submitting states
    const [isSubmitting, setIsSubmitting] = useState(false)

    // File input refs
    const uploadInputRef = useRef<HTMLInputElement>(null)
    const updateInputRef = useRef<HTMLInputElement>(null)

    const client = api(props.accessToken!)


    const fetchReports = async () => {
        try {
            setLoading(true)
            setError(null)
            const data = await client.getReports()
            setReports(data)
        } catch (err) {
            setError('Failed to load reports')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    // Upload new report
    const handleUploadReport = async () => {
        if (!selectedFile) return

        try {
            setIsSubmitting(true)
            setError(null)
            await client.uploadReport(selectedFile)
            setSuccess('Report uploaded successfully')
            setSelectedFile(null)
            setUploadDialogOpen(false)
            if (uploadInputRef.current) {
                uploadInputRef.current.value = ''
            }
            await fetchReports()
        } catch (err) {
            setError('Failed to upload report')
            console.error(err)
        } finally {
            setIsSubmitting(false)
        }
    }

    // Download report
    const handleDownloadReport = async (reportId: number) => {
        try {
            setError(null)
            const blob = await client.downloadReport(reportId)

            // Create download link
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `report_${reportId}.bin`
            document.body.appendChild(a)
            a.click()
            window.URL.revokeObjectURL(url)
            document.body.removeChild(a)

            setSuccess('Report downloaded successfully')
        } catch (err) {
            setError('Failed to download report')
            console.error(err)
        }
    }

    // Update report
    const handleUpdateReport = async () => {
        if (!updateFile || !updatingReportId) return

        try {
            setIsSubmitting(true)
            setError(null)
            await client.updateReport(updatingReportId, updateFile)
            setSuccess('Report updated successfully')
            setUpdateFile(null)
            setUpdatingReportId(null)
            setUpdateDialogOpen(false)
            if (updateInputRef.current) {
                updateInputRef.current.value = ''
            }
            await fetchReports()
        } catch (err) {
            setError('Failed to update report')
            console.error(err)
        } finally {
            setIsSubmitting(false)
        }
    }

    // Delete report
    const handleDeleteReport = async () => {
        if (!deletingReport) return

        try {
            setIsSubmitting(true)
            setError(null)
            await client.deleteReport(deletingReport.id)
            setSuccess('Report deleted successfully')
            setDeleteDialogOpen(false)
            setDeletingReport(null)
            await fetchReports()
        } catch (err) {
            setError('Failed to delete report')
            console.error(err)
        } finally {
            setIsSubmitting(false)
        }
    }

    const openUpdateDialog = (reportId: number) => {
        setUpdatingReportId(reportId)
        setUpdateDialogOpen(true)
    }

    const openDeleteDialog = (report: Report) => {
        setDeletingReport(report)
        setDeleteDialogOpen(true)
    }

    const formatFileSize = (bytes: number) => {
        if (bytes < 1024) return bytes + ' B'
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
    }

    useEffect(() => {
        if (props.accessToken) {
            fetchReports()
        }
    }, [props.accessToken])

    if (loading) {
        return (
            <Container maxWidth="lg" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
                <CircularProgress />
            </Container>
        )
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                <Box>
                    <Typography variant="h4" component="h1" gutterBottom>
                        Reports
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Manage your uploaded reports
                    </Typography>
                </Box>
                <Button
                    variant="contained"
                    startIcon={<CloudUpload />}
                    onClick={() => setUploadDialogOpen(true)}
                >
                    Upload Report
                </Button>
            </Box>

            {/* Success Alert */}
            {success && (
                <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
                    {success}
                </Alert>
            )}

            {/* Error Alert */}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {/* Reports Table */}
            {reports.length === 0 ? (
                <Card>
                    <CardContent>
                        <Box sx={{ textAlign: 'center', py: 8 }}>
                            <Description sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                            <Typography variant="h6" color="text.secondary" gutterBottom>
                                No reports yet
                            </Typography>
                            <Typography color="text.secondary" sx={{ mb: 3 }}>
                                Upload your first report to get started
                            </Typography>
                            <Button
                                variant="contained"
                                startIcon={<CloudUpload />}
                                onClick={() => setUploadDialogOpen(true)}
                            >
                                Upload Report
                            </Button>
                        </Box>
                    </CardContent>
                </Card>
            ) : (
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>ID</TableCell>
                                <TableCell>File Size</TableCell>
                                <TableCell align="right">Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {reports.map((report) => (
                                <TableRow key={report.id} hover>
                                    <TableCell>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Description color="primary" />
                                            <Typography variant="body2">
                                                Report #{report.id}
                                            </Typography>
                                        </Box>
                                    </TableCell>
                                    <TableCell>
                                        <Chip
                                            label={formatFileSize(report.data.length)}
                                            size="small"
                                            variant="outlined"
                                        />
                                    </TableCell>
                                    <TableCell align="right">
                                        <IconButton
                                            size="small"
                                            color="primary"
                                            onClick={() => handleDownloadReport(report.id)}
                                            title="Download"
                                        >
                                            <Download />
                                        </IconButton>
                                        <IconButton
                                            size="small"
                                            color="info"
                                            onClick={() => openUpdateDialog(report.id)}
                                            title="Update"
                                        >
                                            <Edit />
                                        </IconButton>
                                        <IconButton
                                            size="small"
                                            color="error"
                                            onClick={() => openDeleteDialog(report)}
                                            title="Delete"
                                        >
                                            <Delete />
                                        </IconButton>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}

            {/* Upload Report Dialog */}
            <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Upload Report</DialogTitle>
                <DialogContent>
                    <Box sx={{ mt: 2 }}>
                        <input
                            ref={uploadInputRef}
                            type="file"
                            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                            style={{ display: 'none' }}
                            id="upload-file-input"
                        />
                        <label htmlFor="upload-file-input">
                            <Button
                                variant="outlined"
                                component="span"
                                startIcon={<Upload />}
                                fullWidth
                            >
                                Choose File
                            </Button>
                        </label>
                        {selectedFile && (
                            <Box sx={{ mt: 2 }}>
                                <Typography variant="body2" color="text.secondary">
                                    Selected: {selectedFile.name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    Size: {formatFileSize(selectedFile.size)}
                                </Typography>
                            </Box>
                        )}
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setUploadDialogOpen(false)} disabled={isSubmitting}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleUploadReport}
                        variant="contained"
                        disabled={!selectedFile || isSubmitting}
                    >
                        {isSubmitting ? 'Uploading...' : 'Upload'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Update Report Dialog */}
            <Dialog open={updateDialogOpen} onClose={() => setUpdateDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Update Report #{updatingReportId}</DialogTitle>
                <DialogContent>
                    <Box sx={{ mt: 2 }}>
                        <input
                            ref={updateInputRef}
                            type="file"
                            onChange={(e) => setUpdateFile(e.target.files?.[0] || null)}
                            style={{ display: 'none' }}
                            id="update-file-input"
                        />
                        <label htmlFor="update-file-input">
                            <Button
                                variant="outlined"
                                component="span"
                                startIcon={<Upload />}
                                fullWidth
                            >
                                Choose New File
                            </Button>
                        </label>
                        {updateFile && (
                            <Box sx={{ mt: 2 }}>
                                <Typography variant="body2" color="text.secondary">
                                    Selected: {updateFile.name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    Size: {formatFileSize(updateFile.size)}
                                </Typography>
                            </Box>
                        )}
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setUpdateDialogOpen(false)} disabled={isSubmitting}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleUpdateReport}
                        variant="contained"
                        disabled={!updateFile || isSubmitting}
                    >
                        {isSubmitting ? 'Updating...' : 'Update'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Delete Report Dialog */}
            <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Delete Report</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to delete Report #{deletingReport?.id}? This action cannot be undone.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDeleteDialogOpen(false)} disabled={isSubmitting}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleDeleteReport}
                        variant="contained"
                        color="error"
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? 'Deleting...' : 'Delete'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    )
})

export default ReportsPage
