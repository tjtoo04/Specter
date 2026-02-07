import { configs } from "../utils/config"

const fetchWithAuth = async (endpoint: string, options: RequestInit = {}, accessToken: string) => {
    const baseUrl = configs.backendUrl;
    return fetch(`${baseUrl}${endpoint}`, {
        ...options,
        headers: {
            ...options.headers,
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
        },
    }).then(res => {
        if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
        return res.json();
    });
};

export const api = (accessToken: string) => ({
    whoAmI: async () =>
        fetchWithAuth('/api/users/whoami', { method: 'GET' }, accessToken),

    createProject: async (title: string) =>
        fetchWithAuth('/api/projects', {
            method: 'POST',
            body: JSON.stringify({ title }),
        }, accessToken),

    getProjects: async () =>
        fetchWithAuth('/api/projects', {
            method: 'GET'
        }, accessToken),

    updateProject: async (projectId: number, title: string) =>
        fetchWithAuth(`/api/projects/${projectId}`, {
            method: 'PUT',
            body: JSON.stringify({ title }),
        }, accessToken),

    deleteProject: async (projectId: number) =>
        fetchWithAuth(`/api/projects/${projectId}`, {
            method: 'DELETE',
        }, accessToken),

    getProjectDetails: async (projectId: number) =>
        fetchWithAuth(`/api/projects/${projectId}`, {
            method: 'GET',
        }, accessToken),

    searchUsers: async (query: string) =>
        fetchWithAuth(`/api/users/search?q=${encodeURIComponent(query)}`, {
            method: 'GET',
        }, accessToken),

    addUserToProject: async (projectId: number, userId: string) =>
        fetchWithAuth(`/api/projects/${projectId}/users`, {
            method: 'POST',
            body: JSON.stringify({ user_id: userId }),
        }, accessToken),

    removeUserFromProject: async (projectId: number, userId: string) =>
        fetchWithAuth(`/api/projects/${projectId}/users/${userId}`, {
            method: 'DELETE',
        }, accessToken),
});
