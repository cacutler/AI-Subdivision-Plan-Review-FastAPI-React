import { NavLink } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
export function NavBar() {
    const { user, logout } = useAuth();
    if (!user) {
        return null;
    }
    return (
        <header className="navbar">
            <div className="navbar-brand">
                <span className="navbar-mark" aria-hidden="true">▦</span>
                Plan Review
            </div>
            <nav className="navbar-links">
                <NavLink to="/plans" className={({ isActive }) => (isActive ? "active" : "")}>Plans</NavLink>
                <NavLink to="/plans/new" className={({ isActive }) => (isActive ? "active" : "")}>Upload</NavLink>
                {user.status === "admin" && (
                    <NavLink to="/admin/users" className={({ isActive }) => (isActive ? "active" : "")}>Users</NavLink>
                )}
            </nav>
            <div className="navbar-user">
                <span className="navbar-username">
                    {user.first_name} {user.last_name}
                    <span className="role-tag">{user.status}</span>
                </span>
                <button type="button" className="btn-ghost" onClick={logout}>Sign out</button>
            </div>
        </header>
    );
}