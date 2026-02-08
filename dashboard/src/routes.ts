import { createBrowserRouter } from "react-router";
import App from "./App";
import DashboardPage from "./pages/ProjectDashboard";
import ConfigurationsPage from "./pages/Configuration";
import VerifyOTP from "./pages/VerifyOTP";

const router = createBrowserRouter([
    {
        path: "/", Component: App, children: [
            { index: true, Component: DashboardPage },
            { path: '/configurations', Component: ConfigurationsPage },
            // { path: '/login', Component: LoginPage },
            // { path: '/register', Component: RegisterPage }
        ]
    },
    { path: '/verify-otp', Component: VerifyOTP },
]);

export default router
