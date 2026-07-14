import axios from "axios";
export const api = axios.create({ baseURL: "/api" }); // proxy to FastAPI in dev
api.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
api.interceptors.response.use((res) => res, (err) => {
    if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
    }
    return Promise.reject(err);
});
export function apiErrorMessage(err: unknown, fallback = "Something went wrong"): string {
    if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        if (typeof detail === "string") {
            return detail;
        }
        if (Array.isArray(detail) && detail[0]?.msg) {
            return detail[0].msg;
        }
    }
    return fallback;
}