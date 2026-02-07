import "dotenv/config"
import { createAuthClient } from "better-auth/react"
import { configs } from "./config"

export const authClient = createAuthClient({
    baseURL: configs.backendUrl
})
