import './App.css'
import { AuthProvider } from "@propelauth/react";
import { Outlet, useLocation } from 'react-router'
import Sidebar from './components/Sidebar'
import { useEffect, useMemo, useState } from 'react';
import { Box, createTheme, CssBaseline, IconButton, type PaletteMode } from '@mui/material';
import { ThemeProvider } from '@emotion/react';
import { ColorModeContext } from './context/ColorModeContext';
import { Brightness7, Brightness4 } from '@mui/icons-material';
import { configs } from './utils/config';

function App() {
    const [mode, setMode] = useState<PaletteMode>(() => {
        const savedMode = localStorage.getItem('themeMode');
        return (savedMode as PaletteMode) || 'light';
    });

    const colorMode = useMemo(() => ({
        toggleColorMode: () => {
            setMode((prev) => (prev === 'light' ? 'dark' : 'light'));
        },
        mode,
    }), [mode]);

    const theme = useMemo(() => createTheme({
        palette: { mode }, typography: {
            fontFamily: '"FoundersGrotesk", "Helvetica", "Arial", sans-serif',
            button: {
                textTransform: 'none',
            }
        }
    }), [mode]);

    const location = useLocation();

    useEffect(() => {
        localStorage.setItem('themeMode', mode);
    }, [mode]);

    return (
        <AuthProvider
            authUrl={configs.authUrl}
            minSecondsBeforeRefresh={120}
        >
            <ColorModeContext.Provider value={colorMode}>
                <ThemeProvider theme={theme}>
                    <CssBaseline />
                    <div className='app-container' >
                        <nav className='top-nav-bar'>
                            {/* {!noSidebarLocation.find(loc => loc === location.pathname) && */}
                            {/*     <> */}
                            <Sidebar />
                            <IconButton className='theme-toggle' onClick={colorMode.toggleColorMode} color="inherit">
                                {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
                            </IconButton>
                            {/*     </> */}
                            {/* } */}
                        </nav>
                        <Outlet />
                    </div>
                </ThemeProvider>
            </ColorModeContext.Provider>
        </AuthProvider>
    )
}

export default App
