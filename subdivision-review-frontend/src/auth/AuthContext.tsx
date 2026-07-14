import { createContext, useContext, useState, useEffect } from "react";
import { api } from "../api/client";
import type { User } from "../types";
interface AuthState {
    user: User | null;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
    loading: boolean;
}
const AuthContext = createContext<AuthState | null>(null);
export function AuthProvider({children}: {children: React.ReactNode}) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        const token = localStorage.getItem("access_token");
        if (!token) {
            setLoading(false);
            return;
        }
        api.get("/users/me").then(res => setUser(res.data)).catch(() => {
            localStorage.removeItem("access_token");
        }).finally(() => setLoading(false));
    }, []);
    async function login(username: string, password: string) {
        const res = await api.post("/auth/login", {username, password});
        localStorage.setItem("access_token", res.data.access_token);
        const me = await api.get("/users/me");
        setUser(me.data);
    }
    function logout() {
        localStorage.removeItem("access_token");
        setUser(null);
    }
    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}
export const useAuth = () => useContext(AuthContext)!;