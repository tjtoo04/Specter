import './Sidebar.css'
import { AppRegistration, Brightness4, Brightness7, Dashboard, Login, Logout, Menu, Person, PersonAdd, Report, Settings } from "@mui/icons-material";
import { Box, Button, Divider, Drawer, IconButton, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Typography } from "@mui/material";
import { useHostedPageUrls, useLogoutFunction, useRedirectFunctions, withAuthInfo, type WithAuthInfoProps } from '@propelauth/react';
import { useEffect, useState } from "react";
import { Link } from 'react-router';
import { api } from '../lib/api';

const Sidebar = withAuthInfo(
    (props: WithAuthInfoProps) => {
        const logoutFunction = useLogoutFunction()
        const { redirectToLoginPage, redirectToSignupPage, redirectToAccountPage } = useRedirectFunctions()
        const itemList = [
            { text: 'Project Dashboard', icon: <Dashboard /> },
            { text: 'Reports', icon: <Report /> },
            { text: 'Configurations', icon: <Settings /> }
        ]
        const [open, setOpen] = useState(false);

        const toggleDrawer = (newOpen: boolean) => () => {
            setOpen(newOpen);
        };

        const client = api(props.accessToken!)

        useEffect(() => {
            if (props.accessToken) {
                client.whoAmI().then(console.log)
            }

        }, [])

        const DrawerList = (
            <Box sx={{ width: 250 }} role="presentation" className="drawer-list" onClick={toggleDrawer(false)}>
                <div>
                    <h2 className='sidebar-title'> Specter </h2>
                    <List>
                        {itemList.map((item, index) => (
                            <ListItem key={item.text}>
                                <ListItemIcon>
                                    {item.icon}
                                </ListItemIcon>
                                <ListItemButton>
                                    <ListItemText primary={item.text} />
                                </ListItemButton>
                            </ListItem>
                        ))}
                    </List>
                </div>
                <div className='login-button'>
                    {
                        props.isLoggedIn ?
                            <>
                                <IconButton onClick={() => redirectToAccountPage()}>
                                    <Person />
                                </IconButton>
                                <IconButton onClick={() => logoutFunction(true)} >
                                    <Logout />
                                </IconButton>
                            </>
                            :
                            <>
                                <IconButton type='button' onClick={() => redirectToSignupPage()}>
                                    <PersonAdd />
                                </IconButton>
                                <IconButton type='button' onClick={() => redirectToLoginPage()}>
                                    <Login />
                                </IconButton>
                            </>

                    }
                </div>
            </Box>
        );
        return (
            <div className="sidebar-container">
                <Button onClick={() => setOpen(!open)}>
                    <Menu color="primary" />
                </Button>
                <Drawer open={open} onClose={toggleDrawer(false)}>
                    {DrawerList}
                </Drawer>
            </div>
        )
    }
)

export default Sidebar
