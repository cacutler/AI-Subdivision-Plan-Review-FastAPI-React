export type UserRole = "engineer" | "admin";
export type ReviewStatus = "pending" | "processing" | "completed" | "failed";
export type OverallStatus = "pass" | "pass_with_notes" | "fail";
export type Confidence = "high" | "medium" | "low";
export type FindingCategory = "setback" | "lot_coverage" | "easement" | "grading" | "utilities" | "notation" | "other";
export interface Finding {
    id: string;
    category: string;
    description: string;
    code_reference: string | null;
    location_description: string | null;
    page: number | null;
}
export interface DrawingMetadata {
    drawing_type: string | null;
    scale_detected: string | null;
    north_arrow_present: boolean | null;
    legend_present: boolean | null;
}
export interface AIReviewNotes {
    review_version: "1.0";
    reviewed_at: string;
    model: string;
    overall_status: OverallStatus;
    confidence: Confidence;
    summary: string;
    jurisdiction: string | null;
    findings: Finding[];
    drawing_metadata: DrawingMetadata | null;
}
export interface Plan {
    id: string;
    user_id: string;
    title: string;
    file_path: string;
    ai_review_notes: AIReviewNotes | null;
    review_status: ReviewStatus;
    created_at: string;
    updated_at: string;
}
export interface PlanSummary {
    id: string;
    user_id: string;
    title: string;
    review_status: ReviewStatus;
    overall_status: OverallStatus | null;
    created_at: string;
    updated_at: string;
}
export interface User {
    id: string;
    first_name: string;
    last_name: string;
    username: string;
    email: string;
    status: UserRole;
    created_at: string;
}