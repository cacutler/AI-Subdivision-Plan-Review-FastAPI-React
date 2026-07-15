import { useState, type SubmitEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { apiErrorMessage } from "../api/client";
const emptyForm = { first_name: "", last_name: "", username: "", email: "", password: "" };
export function RegisterPage() {
    const { register } = useAuth();
    const navigate = useNavigate();
    const [form, setForm] = useState(emptyForm);
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);
    async function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
        e.preventDefault();
        setError(null);
        if (form.password !== confirmPassword) {
            setError("Passwords do not match");
            return;
        }
        if (form.password.length < 8) {
            setError("Password must be at least 8 characters");
            return;
        }
        setSubmitting(true);
        try {
            await register(form);
            navigate("/plans", { replace: true });
        } catch (err) {
            setError(apiErrorMessage(err, "Could not create your account"));
        } finally {
            setSubmitting(false);
        }
    }
    return (
        <div className="auth-screen">
            <form className="auth-card" onSubmit={handleSubmit}>
                <div className="auth-mark" aria-hidden="true">▦</div>
                <h1>Create account</h1>
                <p className="auth-subtitle">Registers a new engineer account. Admin accounts are created separately by an administrator.</p>
                <div className="field-grid">
                    <label className="field">
                        <span>First name</span>
                        <input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} autoComplete="given-name" required/>
                    </label>
                    <label className="field">
                        <span>Last name</span>
                        <input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} autoComplete="family-name" required/>
                    </label>
                </div>
                <label className="field">
                    <span>Username</span>
                    <input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} autoComplete="username" required/>
                </label>
                <label className="field">
                    <span>Email</span>
                    <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} autoComplete="email" required/>
                </label>
                <label className="field">
                    <span>Password</span>
                    <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} autoComplete="new-password" minLength={8} required/>
                </label>
                <label className="field">
                    <span>Confirm password</span>
                    <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} autoComplete="new-password" minLength={8} required/>
                </label>
                {error && <p className="form-error" role="alert">{error}</p>}
                <button type="submit" className="btn-primary" disabled={submitting}>{submitting ? "Creating account…" : "Create account"}</button>
                <p className="hint" style={{ marginTop: 14 }}>Already have an account? <Link to="/login">Sign in</Link></p>
            </form>
        </div>
    );
}