import { useAuthInfo } from "@propelauth/react"
import { configs } from "../utils/config"

const url = configs.backendUrl

export async function whoAmI(accessToken: string) {
    return fetch('/api/whoami', {
        method: 'GET',
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    }).then((res) => res.json())
}

export const createProject = async (title: string, userId: string) => {
    const res = fetch(`${url}/api/projects`, {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${}`
        }
    })

}
