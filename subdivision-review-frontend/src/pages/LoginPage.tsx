import { useState, type SubmitEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { apiErrorMessage } from "../api/client";
export function LoginPage() {
    const { login } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const from = (location.state as { from?: Location })?.from?.pathname ?? "/plans";
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);
    async function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
        e.preventDefault();
        setError(null);
        setSubmitting(true);
        try {
            await login(username, password);
            navigate(from, {replace: true});
        } catch (err) {
            setError(apiErrorMessage(err, "Invalid username or password"));
        } finally {
            setSubmitting(false);
        }
    }
    return (
        <div className="auth-screen">
            <form className="auth-card" onSubmit={handleSubmit}>
                <div className="auth-mark" aria-hidden="true">▦</div>
                <h1>Plan Review</h1>
                <p className="auth-subtitle">Sign in to review subdivision plans</p>
                <label className="field">
                    <span>Username</span>
                    <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" autoFocus required/>
                </label>
                <label className="field">
                    <span>Password</span>
                    <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required/>
                </label>
                {error && <p className="form-error" role="alert">{error}</p>}
                <button type="submit" className="btn-primary" disabled={submitting}>{submitting ? "Signing in…" : "Sign in"}</button>
                <p className="hint" style={{ marginTop: 14 }}>Don't have an account? <Link to="/register">Register</Link></p>
            </form>
        </div>
    );
}