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

export interface Configuration {
    id: number;
    context: string;
    user: User;
    project: Project;
}

export interface Report {
    id: number;
    data: string; // Base64 
}


export interface ReportMetadata {
    id: number;
    size?: number;
}


export type ReportData = Report[];
export type ConfigurationData = Configuration[];
export type ProjectData = Project[];
