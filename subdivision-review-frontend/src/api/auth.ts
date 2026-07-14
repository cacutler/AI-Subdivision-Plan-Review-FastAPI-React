import { api } from "./client";
import type { User } from "../types";
export interface LoginResponse {
    access_token: string;
    token_type: "bearer";
}
export async function login(username: string, password: string): Promise<LoginResponse> {
    const res = await api.post<LoginResponse>("/auth/login", {username, password});
    return res.data;
}
export async function getMe(): Promise<User> {
    const res = await api.get<User>("/users/me");
    return res.data;
}