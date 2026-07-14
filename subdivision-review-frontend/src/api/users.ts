import { api } from "./client";
import type { User, UserRole } from "../types";
export async function listUsers(params?: { skip?: number; limit?: number }): Promise<User[]> {
    const res = await api.get<User[]>("/users", { params });
    return res.data;
}
export interface CreateUserBody {
    first_name: string;
    last_name: string;
    username: string;
    email: string;
    password: string;
    status: UserRole;
}
export async function createUser(body: CreateUserBody): Promise<User> {
    const res = await api.post<User>("/users", body);
    return res.data;
}
export async function updateUserStatus(userId: string, status: UserRole): Promise<User> {
    const res = await api.put<User>(`/users/${userId}`, { status });
    return res.data;
}
export async function deleteUser(userId: string): Promise<void> {
    await api.delete(`/users/${userId}`);
}