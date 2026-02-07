import { createBrowserRouter } from "react-router";
import App from "./App";
import DashboardPage from "./pages/ProjectDashboard";

const router = createBrowserRouter([
    {
        path: "/", Component: App, children: [
            { index: true, Component: DashboardPage },
            // { path: '/login', Component: LoginPage },
            // { path: '/register', Component: RegisterPage }
        ]
    },
]);

export default router
