import { type WithAuthInfoProps, withAuthInfo } from '@propelauth/react'
import { useEffect } from 'react'
import { whoAmI } from '../lib/api'
import { Container } from '@mui/material'

const DashboardPage = withAuthInfo((props: WithAuthInfoProps) => {
    useEffect(() => {
        whoAmI(props.accessToken ?? '').then(data => console.log(data))
    }, [props.accessToken])

    return (
        <Container maxWidth={false}>
        </Container>
    )

})

export default DashboardPage

