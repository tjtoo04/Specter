import { createBrowserRouter } from "react-router";
import App from "./App";
import Home from "./pages/Home";
import LoginPage from "./pages/Login";
import RegisterPage from "./pages/Register";
import DashboardPage from "./pages/Dashboard";

const router = createBrowserRouter([
    {
        path: "/", Component: App, children: [
            { index: true, Component: DashboardPage },
            { path: '/login', Component: LoginPage },
            { path: '/register', Component: RegisterPage }
        ]
    },
]);

export default router
