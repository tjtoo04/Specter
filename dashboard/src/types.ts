import type { PaletteMode } from "@mui/material";

export interface ColorModeContextType {
    toggleColorMode: () => void;
    mode: PaletteMode;
}

export interface User {
    id: string;
    username: string;
    email: string
}

export interface Project {
    id: number;
    title: string;
    users?: User[];
}

export type ProjectData = Project[];
