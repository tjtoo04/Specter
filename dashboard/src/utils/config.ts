import 'dotenv/config'
const mode = process.env.VITE_APP_MODE
export const configs = {
    backendUrl: mode === 'dev' ? process.env.VITE_BACKEND_URL_DEV : process.env.VITE_BACKEND_URL_PROD,
    frontendUrl: mode === 'dev' ? process.env.VITE_FRONTEND_URL_DEV : process.env.VITE_FRONTEND_URL_PROD
}
