import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listPlans } from "../api/plans";
import { apiErrorMessage } from "../api/client";
import { ReviewStatusBadge, OverallStatusBadge } from "../components/StatusBadge";
import type { PlanSummary } from "../types";
export function PlansListPage() {
    const [plans, setPlans] = useState<PlanSummary[] | null>(null);
    const [error, setError] = useState<string | null>(null);
    useEffect(() => {
        listPlans().then(setPlans).catch((err) => setError(apiErrorMessage(err, "Could not load plans")));
    }, []);
    return (
        <div className="page">
            <div className="page-header">
                <h1>Plans</h1>
                <Link to="/plans/new" className="btn-primary">Upload plan</Link>
            </div>
            {error && <p className="form-error">{error}</p>}
            {!plans && !error && <p className="page-loading">Loading plans…</p>}
            {plans && plans.length === 0 && (
                <div className="empty-state">
                    <p>No plans yet.</p>
                    <Link to="/plans/new">Upload the first one</Link>
                </div>
            )}
            {plans && plans.length > 0 && (
                <table className="plans-table">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Review status</th>
                            <th>Outcome</th>
                            <th>Uploaded</th>
                        </tr>
                    </thead>
                    <tbody>
                        {plans.map((plan) => (
                            <tr key={plan.id}>
                                <td>
                                    <Link to={`/plans/${plan.id}`}>{plan.title}</Link>
                                </td>
                                <td>
                                    <ReviewStatusBadge status={plan.review_status}/>
                                </td>
                                <td>{plan.overall_status ? <OverallStatusBadge status={plan.overall_status}/> : "—"}</td>
                                <td>{new Date(plan.created_at).toLocaleDateString()}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}