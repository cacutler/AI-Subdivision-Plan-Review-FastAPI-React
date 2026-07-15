import { useEffect, useState, type FormEvent } from "react";
import { createUser, deleteUser, listUsers, updateUserStatus } from "../api/users";
import { apiErrorMessage } from "../api/client";
import type { User, UserRole } from "../types";
const emptyForm = { first_name: "", last_name: "", username: "", email: "", password: "", status: "engineer" as UserRole };
export function AdminUsersPage() {
    const [users, setUsers] = useState<User[] | null>(null);
    const [form, setForm] = useState(emptyForm);
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);
    function refresh() {
        listUsers().then(setUsers).catch((err) => setError(apiErrorMessage(err, "Could not load users")));
    }
    useEffect(refresh, []);
    async function handleCreate(e: FormEvent) {
        e.preventDefault();
        setError(null);
        setSubmitting(true);
        try {
            await createUser(form);
            setForm(emptyForm);
            refresh();
        } catch (err) {
            setError(apiErrorMessage(err, "Could not create user"));
        } finally {
            setSubmitting(false);
        }
    }
    async function handleRoleToggle(user: User) {
        const next: UserRole = user.status === "admin" ? "engineer" : "admin";
        await updateUserStatus(user.id, next);
        refresh();
    }
    async function handleDelete(user: User) {
        if (!window.confirm(`Delete user ${user.username}? This cannot be undone.`)) {
            return;
        }
        await deleteUser(user.id);
        refresh();
    }
    return (
        <div className="page">
            <h1>Users</h1>
            <form className="card-form" onSubmit={handleCreate}>
                <h2>Add user</h2>
                <div className="field-grid">
                    <label className="field">
                        <span>First name</span>
                        <input value={form.first_name} onChange={(e) => setForm({...form, first_name: e.target.value})} required/>
                    </label>
                    <label className="field">
                        <span>Last name</span>
                        <input value={form.last_name} onChange={(e) => setForm({...form, last_name: e.target.value})} required/>
                    </label>
                    <label className="field">
                        <span>Username</span>
                        <input value={form.username} onChange={(e) => setForm({...form, username: e.target.value})} required/>
                    </label>
                    <label className="field">
                        <span>Email</span>
                        <input type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} required/>
                    </label>
                    <label className="field">
                        <span>Password</span>
                        <input type="password" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})} required minLength={8}/>
                    </label>
                    <label className="field">
                        <span>Role</span>
                        <select value={form.status} onChange={(e) => setForm({...form, status: e.target.value as UserRole})}>
                            <option value="engineer">Engineer</option>
                            <option value="admin">Admin</option>
                        </select>
                    </label>
                </div>
                {error && <p className="form-error" role="alert">{error}</p>}
                <button type="submit" className="btn-primary" disabled={submitting}>{submitting ? "Creating…" : "Create user"}</button>
            </form>
            {!users && <p className="page-loading">Loading users…</p>}
            {users && (
                <table className="plans-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map((user) => (
                            <tr key={user.id}>
                                <td>{user.first_name} {user.last_name}</td>
                                <td>{user.username}</td>
                                <td>{user.email}</td>
                                <td>
                                    <button type="button" className="btn-ghost" onClick={() => handleRoleToggle(user)}>{user.status}</button>
                                </td>
                                <td>
                                    <button type="button" className="btn-ghost btn-danger" onClick={() => handleDelete(user)}>Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}