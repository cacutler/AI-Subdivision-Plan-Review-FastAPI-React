import { api } from "./client";
import type { Plan, PlanSummary } from "../types";
export async function listPlans(params?: { skip?: number; limit?: number }): Promise<PlanSummary[]> {
    const res = await api.get<PlanSummary[]>("/plans", { params });
    return res.data;
}
export async function getPlan(planId: string): Promise<Plan> {
    const res = await api.get<Plan>(`/plans/${planId}`);
    return res.data;
}
export async function uploadPlan(title: string, file: File): Promise<Plan> {
    const form = new FormData();
    form.append("file", file);
    const res = await api.post<Plan>("/plans", form, {
        params: {title},
        headers: {"Content-Type": "multipart/form-data"}
    });
    return res.data;
}
export async function updatePlanTitle(planId: string, title: string): Promise<Plan> {
    const res = await api.put<Plan>(`/plans/${planId}`, { title });
    return res.data;
}
export async function deletePlan(planId: string): Promise<void> {
    await api.delete(`/plans/${planId}`);
}
export async function triggerReview(planId: string, jurisdiction?: string): Promise<Plan> {
    const res = await api.post<Plan>(`/plans/${planId}/review`, null, {
        params: jurisdiction ? {jurisdiction} : undefined,
    });
    return res.data;
}