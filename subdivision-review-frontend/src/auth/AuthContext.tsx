import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { getMe, login as loginRequest } from "../api/auth";
import type { User } from "../types";
interface AuthContextValue {
    user: User | null;
    loading: boolean;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
}
const AuthContext = createContext<AuthContextValue | null>(null);
export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        const token = localStorage.getItem("access_token");
        if (!token) {
            setLoading(false);
            return;
        }
        getMe().then(setUser).catch(() => localStorage.removeItem("access_token")).finally(() => setLoading(false));
    }, []);
    async function login(username: string, password: string) {
        const {access_token} = await loginRequest(username, password);
        localStorage.setItem("access_token", access_token);
        const me = await getMe();
        setUser(me);
    }
    function logout() {
        localStorage.removeItem("access_token");
        setUser(null);
    }
    return (
        <AuthContext.Provider value={{user, loading, login, logout}}>
            {children}
        </AuthContext.Provider>
    );
}
export function useAuth(): AuthContextValue {
    const ctx = useContext(AuthContext);
    if (!ctx) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return ctx;
}