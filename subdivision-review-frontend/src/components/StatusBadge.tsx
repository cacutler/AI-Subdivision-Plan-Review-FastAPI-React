import type { OverallStatus, ReviewStatus } from "../types";
const REVIEW_STATUS_LABEL: Record<ReviewStatus, string> = {pending: "Pending", processing: "Reviewing…", completed: "Reviewed", failed: "Review failed"};
const OVERALL_STATUS_LABEL: Record<OverallStatus, string> = {pass: "Pass", pass_with_notes: "Pass with notes", fail: "Fail"};
export function ReviewStatusBadge({ status }: { status: ReviewStatus }) {
    return <span className={`badge badge-review-${status}`}>{REVIEW_STATUS_LABEL[status]}</span>;
}
export function OverallStatusBadge({ status }: { status: OverallStatus }) {
    return <span className={`badge badge-overall-${status}`}>{OVERALL_STATUS_LABEL[status]}</span>;
}