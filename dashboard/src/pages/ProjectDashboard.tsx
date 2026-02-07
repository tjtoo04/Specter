import { type WithAuthInfoProps, withAuthInfo } from '@propelauth/react'
import { useDebouncedCallback } from 'use-debounce';
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
    Grid,
    List,
    ListItem,
    ListItemText,
} from '@mui/material'
import { Add, Edit, Delete, Visibility, PersonAdd, Close } from '@mui/icons-material'
import { api } from '../lib/api'
import type { Project, ProjectData, User } from '../types'

const DashboardPage = withAuthInfo((props: WithAuthInfoProps) => {
    const [projects, setProjects] = useState<ProjectData>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    // Dialog states
    const [createDialogOpen, setCreateDialogOpen] = useState(false)
    const [editDialogOpen, setEditDialogOpen] = useState(false)
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
    const [detailsDialogOpen, setDetailsDialogOpen] = useState(false)

    // Form states
    const [newProjectTitle, setNewProjectTitle] = useState('')
    const [editingProject, setEditingProject] = useState<Project | null>(null)
    const [editProjectTitle, setEditProjectTitle] = useState('')
    const [deletingProject, setDeletingProject] = useState<Project | null>(null)
    const [viewingProject, setViewingProject] = useState<Project | null>(null)
    const [loadingDetails, setLoadingDetails] = useState(false)

    // Add user states
    const [addUserDialogOpen, setAddUserDialogOpen] = useState(false)
    const [userSearchQuery, setUserSearchQuery] = useState('')
    const [searchResults, setSearchResults] = useState<User[]>([])
    const [searchingUsers, setSearchingUsers] = useState(false)

    // Submitting states
    const [isSubmitting, setIsSubmitting] = useState(false)

    const client = api(props.accessToken!)

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

    const handleCreateProject = async () => {
        if (!newProjectTitle.trim()) return

        try {
            setIsSubmitting(true)
            setError(null)
            await client.createProject(newProjectTitle)
            setNewProjectTitle('')
            setCreateDialogOpen(false)
            await fetchProjects()
        } catch (err) {
            setError('Failed to create project')
            console.error(err)
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleUpdateProject = async () => {
        if (!editingProject || !editProjectTitle.trim()) return

        try {
            setIsSubmitting(true)
            setError(null)
            await client.updateProject(editingProject.id, editProjectTitle)
            setEditDialogOpen(false)
            setEditingProject(null)
            setEditProjectTitle('')
            await fetchProjects()
        } catch (err) {
            setError('Failed to update project')
            console.error(err)
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleDeleteProject = async () => {
        if (!deletingProject) return

        try {
            setIsSubmitting(true)
            setError(null)
            await client.deleteProject(deletingProject.id)
            setDeleteDialogOpen(false)
            setDeletingProject(null)
            await fetchProjects()
        } catch (err) {
            setError('Failed to delete project')
            console.error(err)
        } finally {
            setIsSubmitting(false)
        }
    }

    const openEditDialog = (project: Project) => {
        setEditingProject(project)
        setEditProjectTitle(project.title)
        setEditDialogOpen(true)
    }

    const openDeleteDialog = (project: Project) => {
        setDeletingProject(project)
        setDeleteDialogOpen(true)
    }

    const openDetailsDialog = async (project: Project) => {
        setViewingProject(project)
        setDetailsDialogOpen(true)
        setLoadingDetails(true)

        try {
            const detailedProject = await client.getProjectDetails(project.id)
            setViewingProject(detailedProject)
        } catch (err) {
            setError('Failed to load project details')
            console.error(err)
        } finally {
            setLoadingDetails(false)
        }
    }

    const searchUsers = async (query: string) => {
        if (query.length < 2) {
            setSearchResults([])
            return
        }

        try {
            setSearchingUsers(true)
            const results = await client.searchUsers(query)
            setSearchResults(results)
        } catch (err) {
            console.error('Failed to search users:', err)
        } finally {
            setSearchingUsers(false)
        }
    }

    const debouncedSearchUsers = useDebouncedCallback(
        searchUsers,
        500 // 500ms delay
    )

    const handleSearchUsers = (query: string) => {
        setUserSearchQuery(query)
        if (query.length < 2) {
            setSearchResults([])
            setSearchingUsers(false)
            return
        }
        setSearchingUsers(true)
        debouncedSearchUsers(query)
    }

    const handleAddUser = async (userId: string) => {
        if (!viewingProject) return

        try {
            setIsSubmitting(true)
            setError(null)
            const updatedProject = await client.addUserToProject(viewingProject.id, userId)
            setViewingProject(updatedProject)
            setUserSearchQuery('')
            setSearchResults([])
            setAddUserDialogOpen(false)
            await fetchProjects()
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to add user to project'
            setError(errorMessage)
            console.error(err)
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleRemoveUser = async (userId: string) => {
        if (!viewingProject) return

        try {
            setIsSubmitting(true)
            setError(null)
            const updatedProject = await client.removeUserFromProject(viewingProject.id, userId)
            setViewingProject(updatedProject)
            await fetchProjects()
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to remove user from project'
            setError(errorMessage)
            console.error(err)
        } finally {
            setIsSubmitting(false)
        }
    }

    useEffect(() => {
        if (props.accessToken) {
            fetchProjects()
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
                <Typography variant="h4" component="h1">
                    My Projects
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => setCreateDialogOpen(true)}
                >
                    New Project
                </Button>
            </Box>

            {/* Error Alert */}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {/* Projects Grid */}
            {projects.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                        No projects yet
                    </Typography>
                    <Typography color="text.secondary" sx={{ mb: 3 }}>
                        Create your first project to get started
                    </Typography>
                    <Button
                        variant="contained"
                        startIcon={<Add />}
                        onClick={() => setCreateDialogOpen(true)}
                    >
                        Create Project
                    </Button>
                </Box>
            ) : (
                <Grid container spacing={3}>
                    {projects.map((project) => (
                        <Grid size={{ xs: 12, sm: 6, md: 4 }} key={project.id}>
                            <Card
                                sx={{
                                    cursor: 'pointer',
                                    transition: 'all 0.2s',
                                    '&:hover': {
                                        transform: 'translateY(-4px)',
                                        boxShadow: 4,
                                    }
                                }}
                            >
                                <CardContent onClick={() => openDetailsDialog(project)}>
                                    <Typography variant="h6" component="h2">
                                        {project.title}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        ID: {project.id}
                                    </Typography>
                                </CardContent>
                                <CardActions sx={{ justifyContent: 'flex-end' }}>
                                    <IconButton
                                        size="small"
                                        color="primary"
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            openEditDialog(project)
                                        }}
                                    >
                                        <Edit />
                                    </IconButton>
                                    <IconButton
                                        size="small"
                                        color="error"
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            openDeleteDialog(project)
                                        }}
                                    >
                                        <Delete />
                                    </IconButton>
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}

            {/* Create Project Dialog */}
            <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Create New Project</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Project Title"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={newProjectTitle}
                        onChange={(e) => setNewProjectTitle(e.target.value)}
                        onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                                handleCreateProject()
                            }
                        }}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setCreateDialogOpen(false)} disabled={isSubmitting}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleCreateProject}
                        variant="contained"
                        disabled={!newProjectTitle.trim() || isSubmitting}
                    >
                        {isSubmitting ? 'Creating...' : 'Create'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Edit Project Dialog */}
            <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Edit Project</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Project Title"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={editProjectTitle}
                        onChange={(e) => setEditProjectTitle(e.target.value)}
                        onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                                handleUpdateProject()
                            }
                        }}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setEditDialogOpen(false)} disabled={isSubmitting}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleUpdateProject}
                        variant="contained"
                        disabled={!editProjectTitle.trim() || isSubmitting}
                    >
                        {isSubmitting ? 'Saving...' : 'Save'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Delete Project Dialog */}
            <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Delete Project</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to delete "{deletingProject?.title}"? This action cannot be undone.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDeleteDialogOpen(false)} disabled={isSubmitting}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleDeleteProject}
                        variant="contained"
                        color="error"
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? 'Deleting...' : 'Delete'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Project Details Dialog */}
            <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Visibility />
                            Project Details
                        </Box>
                        <IconButton
                            size="small"
                            onClick={() => setDetailsDialogOpen(false)}
                        >
                            <Close />
                        </IconButton>
                    </Box>
                </DialogTitle>
                <DialogContent>
                    {loadingDetails ? (
                        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                            <CircularProgress />
                        </Box>
                    ) : viewingProject ? (
                        <Box>
                            <Box sx={{ mb: 3 }}>
                                <Typography variant="overline" color="text.secondary">
                                    Title
                                </Typography>
                                <Typography variant="h6">
                                    {viewingProject.title}
                                </Typography>
                            </Box>

                            <Box sx={{ mb: 3 }}>
                                <Typography variant="overline" color="text.secondary">
                                    Project ID
                                </Typography>
                                <Typography>
                                    {viewingProject.id}
                                </Typography>
                            </Box>

                            <Box>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                    <Typography variant="overline" color="text.secondary">
                                        Team Members ({viewingProject.users?.length || 0})
                                    </Typography>
                                    <Button
                                        size="small"
                                        startIcon={<PersonAdd />}
                                        onClick={() => setAddUserDialogOpen(true)}
                                    >
                                        Add User
                                    </Button>
                                </Box>
                                {viewingProject.users && viewingProject.users.length > 0 ? (
                                    <List dense>
                                        {viewingProject.users.map((user) => (
                                            <ListItem
                                                key={user.id}
                                                sx={{ px: 0 }}
                                                secondaryAction={
                                                    viewingProject.users && viewingProject.users.length > 1 ? (
                                                        <IconButton
                                                            edge="end"
                                                            size="small"
                                                            onClick={() => handleRemoveUser(user.id)}
                                                            disabled={isSubmitting}
                                                        >
                                                            <Close fontSize="small" />
                                                        </IconButton>
                                                    ) : null
                                                }
                                            >
                                                <ListItemText
                                                    primary={user.username}
                                                    secondary={user.email}
                                                />
                                            </ListItem>
                                        ))}
                                    </List>
                                ) : (
                                    <Typography color="text.secondary">
                                        No team members yet
                                    </Typography>
                                )}
                            </Box>
                        </Box>
                    ) : null}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDetailsDialogOpen(false)}>
                        Close
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Add User Dialog */}
            <Dialog open={addUserDialogOpen} onClose={() => setAddUserDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Add User to Project</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Search by email or username"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={userSearchQuery}
                        onChange={(e) => handleSearchUsers(e.target.value)}
                        placeholder="Start typing to search..."
                    />

                    <Box sx={{ mt: 2 }}>
                        {searchingUsers ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                                <CircularProgress size={24} />
                            </Box>
                        ) : searchResults.length > 0 ? (
                            <List>
                                {searchResults.map((user) => (
                                    <ListItem
                                        key={user.id}
                                        secondaryAction={
                                            <Button
                                                size="small"
                                                variant="outlined"
                                                onClick={() => handleAddUser(user.id)}
                                                disabled={isSubmitting}
                                            >
                                                Add
                                            </Button>
                                        }
                                    >
                                        <ListItemText
                                            primary={user.username}
                                            secondary={user.email}
                                        />
                                    </ListItem>
                                ))}
                            </List>
                        ) : userSearchQuery.length >= 2 ? (
                            <Typography color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                                No users found
                            </Typography>
                        ) : (
                            <Typography color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                                Type at least 2 characters to search
                            </Typography>
                        )}
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => {
                        setAddUserDialogOpen(false)
                        setUserSearchQuery('')
                        setSearchResults([])
                    }}>
                        Cancel
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    )
})

export default DashboardPage
