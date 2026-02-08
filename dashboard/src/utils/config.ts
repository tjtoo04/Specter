const mode = import.meta.env.VITE_APP_MODE
export const configs = {
    backendUrl: mode === 'dev' ? import.meta.env.VITE_BACKEND_URL_DEV : import.meta.env.VITE_BACKEND_URL_PROD,
    frontendUrl: mode === 'dev' ? import.meta.env.VITE_FRONTEND_URL_DEV : import.meta.env.VITE_FRONTEND_URL_PROD,
    authUrl: import.meta.env.VITE_AUTH_URL
}
