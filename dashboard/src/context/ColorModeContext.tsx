import { createContext, useContext } from 'react';
import type { ColorModeContextType } from '../types';

export const ColorModeContext = createContext<ColorModeContextType>({
    toggleColorMode: () => { },
    mode: 'light',
});

export const useColorMode = () => useContext(ColorModeContext);
