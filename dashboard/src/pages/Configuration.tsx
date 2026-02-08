import { type WithAuthInfoProps, withAuthInfo } from '@propelauth/react'
import { useEffect, useState } from 'react'
import {
    Container,
    Box,
    Typography,
    Button,
    Card,
    CardContent,
    CardActions,
    TextField,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    IconButton,
    Alert,
    CircularProgress,
    MenuItem,
    Select,
    FormControl,
    InputLabel,
    Chip,
} from '@mui/material'
import { Add, Edit, Delete, Settings } from '@mui/icons-material'
import { api } from '../lib/api'
import type { Project, Configuration, ConfigurationData } from '../types'
import { useColorMode } from '../context/ColorModeContext'

const ConfigurationsPage = withAuthInfo((props: WithAuthInfoProps) => {
    const [projects, setProjects] = useState<Project[]>([])
    const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null)
    const [configurations, setConfigurations] = useState<ConfigurationData>([])
    const [loading, setLoading] = useState(true)
    const [loadingConfigs, setLoadingConfigs] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Dialog states
    const [createDialogOpen, setCreateDialogOpen] = useState(false)
    const [editDialogOpen, setEditDialogOpen] = useState(false)
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)

    // Form states
    const [newConfigContext, setNewConfigContext] = useState('')
    const [editingConfig, setEditingConfig] = useState<Configuration | null>(null)
    const [editConfigContext, setEditConfigContext] = useState('')
    const [deletingConfig, setDeletingConfig] = useState<Configuration | null>(null)

    // Submitting states
    const [isSubmitting, setIsSubmitting] = useState(false)

    const client = api(props.accessToken!)
    const { mode } = useColorMode()

    const fetchProjects = async () => {
        try {
            setLoading(true)
            setError(null)
            const data = await client.getProjects()
            setProjects(data)
        } catch (err) {
            setError('Failed to load projects')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const fetchConfigurations = async (projectId: number) => {
        try {
            setLoadingConfigs(true)
            setError(null)
            const data = await client.getProjectConfigurations(projectId)
            console.log(data)
            setConfigurations(data)
        } catch (err) {
            setError('Failed to load configurations')
            console.error(err)
        } finally {
            setLoadingConfigs(false)
        }
    }

    const handleCreateConfiguration = async () => {
        if (!newConfigContext.trim() || !selectedProjectId) return

        try {
            setIsSubmitting(true)
            setError(null)
            await client.createConfiguration(selectedProjectId, newConfigContext)
            setNewConfigContext('')
            setCreateDialogOpen(false)
            await fetchConfigurations(selectedProjectId)
        } catch (err) {
            setError('Failed to create configuration')
            console.error(err)
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleUpdateConfiguration = async () => {
        if (!editingConfig || !editConfigContext.trim()) return

        try {
            setIsSubmitting(true)
            setError(null)
            await client.updateConfiguration(editingConfig.id, editConfigContext)
            setEditDialogOpen(false)
            setEditingConfig(null)
            setEditConfigContext('')
            if (selectedProjectId) {
                await fetchConfigurations(selectedProjectId)
            }
        } catch (err) {
            setError('Failed to update configuration')
            console.error(err)
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleDeleteConfiguration = async () => {
        if (!deletingConfig) return

        try {
            setIsSubmitting(true)
            setError(null)
            await client.deleteConfiguration(deletingConfig.id)
            setDeleteDialogOpen(false)
            setDeletingConfig(null)
            if (selectedProjectId) {
                await fetchConfigurations(selectedProjectId)
            }
        } catch (err) {
            setError('Failed to delete configuration')
            console.error(err)
        } finally {
            setIsSubmitting(false)
        }
    }

    const openEditDialog = (config: Configuration) => {
        setEditingConfig(config)
        setEditConfigContext(config.context)
        setEditDialogOpen(true)
    }

    const openDeleteDialog = (config: Configuration) => {
        setDeletingConfig(config)
        setDeleteDialogOpen(true)
    }

    useEffect(() => {
        if (props.accessToken) {
            fetchProjects()
        }
    }, [props.accessToken])

    useEffect(() => {
        if (selectedProjectId) {
            fetchConfigurations(selectedProjectId)
        } else {
            setConfigurations([])
        }
    }, [selectedProjectId])

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
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Configurations
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    Manage configurations for your projects
                </Typography>
            </Box>

            {/* Error Alert */}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {/* Project Selector */}
            <Card sx={{ mb: 4 }}>
                <CardContent>
                    <FormControl fullWidth>
                        <InputLabel id="project-select-label">Select Project</InputLabel>
                        <Select
                            labelId="project-select-label"
                            value={selectedProjectId || ''}
                            label="Select Project"
                            onChange={(e) => setSelectedProjectId(Number(e.target.value))}
                        >
                            {projects.map((project) => (
                                <MenuItem key={project.id} value={project.id}>
                                    {project.title}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </CardContent>
            </Card>

            {/* Configurations Section */}
            {selectedProjectId ? (
                <>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                        <Typography variant="h5" component="h2">
                            Configurations
                            {configurations.length > 0 && (
                                <Chip
                                    label={configurations.length}
                                    size="small"
                                    sx={{ ml: 2 }}
                                />
                            )}
                        </Typography>
                        <Button
                            variant="contained"
                            startIcon={<Add />}
                            onClick={() => setCreateDialogOpen(true)}
                        >
                            New Configuration
                        </Button>
                    </Box>

                    {loadingConfigs ? (
                        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                            <CircularProgress />
                        </Box>
                    ) : configurations.length === 0 ? (
                        <Card>
                            <CardContent>
                                <Box sx={{ textAlign: 'center', py: 4 }}>
                                    <Settings sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                                    <Typography variant="h6" color="text.secondary" gutterBottom>
                                        No configurations yet
                                    </Typography>
                                    <Typography color="text.secondary" sx={{ mb: 3 }}>
                                        Create your first configuration for this project
                                    </Typography>
                                    <Button
                                        variant="contained"
                                        startIcon={<Add />}
                                        onClick={() => setCreateDialogOpen(true)}
                                    >
                                        Create Configuration
                                    </Button>
                                </Box>
                            </CardContent>
                        </Card>
                    ) : (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            {configurations.map((config) => (
                                <Card key={config.id}>
                                    <CardContent>
                                        <Box sx={{ mb: 2 }}>
                                            <Typography variant="overline" color="text.secondary">
                                                Configuration #{config.id}
                                            </Typography>
                                        </Box>
                                        <Typography
                                            variant="body1"
                                            sx={{
                                                whiteSpace: 'pre-wrap',
                                                wordBreak: 'break-word',
                                                fontFamily: 'monospace',
                                                bgcolor: mode === 'light' ? 'grey.100' : 'grey.800',
                                                p: 2,
                                                borderRadius: 1,
                                            }}
                                        >
                                            {config.context}
                                        </Typography>
                                    </CardContent>
                                    <CardActions sx={{ justifyContent: 'flex-end' }}>
                                        <IconButton
                                            size="small"
                                            color="primary"
                                            onClick={() => openEditDialog(config)}
                                        >
                                            <Edit />
                                        </IconButton>
                                        <IconButton
                                            size="small"
                                            color="error"
                                            onClick={() => openDeleteDialog(config)}
                                        >
                                            <Delete />
                                        </IconButton>
                                    </CardActions>
                                </Card>
                            ))}
                        </Box>
                    )}
                </>
            ) : (
                <Card>
                    <CardContent>
                        <Box sx={{ textAlign: 'center', py: 4 }}>
                            <Settings sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                            <Typography variant="h6" color="text.secondary">
                                Select a project to manage configurations
                            </Typography>
                        </Box>
                    </CardContent>
                </Card>
            )}

            {/* Create Configuration Dialog */}
            <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
                <DialogTitle>Create New Configuration</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Context"
                        type="text"
                        fullWidth
                        multiline
                        rows={6}
                        variant="outlined"
                        value={newConfigContext}
                        onChange={(e) => setNewConfigContext(e.target.value)}
                        placeholder="Enter configuration context..."
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setCreateDialogOpen(false)} disabled={isSubmitting}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleCreateConfiguration}
                        variant="contained"
                        disabled={!newConfigContext.trim() || isSubmitting}
                    >
                        {isSubmitting ? 'Creating...' : 'Create'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Edit Configuration Dialog */}
            <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
                <DialogTitle>Edit Configuration</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Context"
                        type="text"
                        fullWidth
                        multiline
                        rows={6}
                        variant="outlined"
                        value={editConfigContext}
                        onChange={(e) => setEditConfigContext(e.target.value)}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setEditDialogOpen(false)} disabled={isSubmitting}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleUpdateConfiguration}
                        variant="contained"
                        disabled={!editConfigContext.trim() || isSubmitting}
                    >
                        {isSubmitting ? 'Saving...' : 'Save'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Delete Configuration Dialog */}
            <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Delete Configuration</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to delete configuration #{deletingConfig?.id}? This action cannot be undone.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDeleteDialogOpen(false)} disabled={isSubmitting}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleDeleteConfiguration}
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

export default ConfigurationsPage
