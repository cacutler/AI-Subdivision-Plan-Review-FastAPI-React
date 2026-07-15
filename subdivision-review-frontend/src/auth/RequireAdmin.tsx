import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./AuthContext";
export function RequireAdmin() {
    const { user, loading } = useAuth();
    if (loading) {
        return <div className="page-loading">Loading…</div>;
    }
    if (!user) {
        return <Navigate to="/login" replace/>;
    }
    if (user.status !== "admin") {
        return <Navigate to="/plans" replace/>;
    }
    return <Outlet/>;
}