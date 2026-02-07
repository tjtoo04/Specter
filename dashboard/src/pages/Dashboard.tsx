import { type WithAuthInfoProps, withAuthInfo } from '@propelauth/react'

const DashboardPage = withAuthInfo((props: WithAuthInfoProps) => {
    if (props.isLoggedIn) {
        return <p>You are logged in as {props.user.email}</p>
    } else {
        return <p>You are not logged in</p>
    }
})

export default DashboardPage

