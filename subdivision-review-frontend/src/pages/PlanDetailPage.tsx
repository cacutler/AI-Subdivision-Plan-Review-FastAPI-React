import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { deletePlan, getPlan, triggerReview } from "../api/plans";
import { apiErrorMessage } from "../api/client";
import { ReviewStatusBadge, OverallStatusBadge } from "../components/StatusBadge";
import { FindingCard } from "../components/FindingCard";
import type { Plan } from "../types";

export function PlanDetailPage() {
  const { planId } = useParams<{ planId: string }>();
  const navigate = useNavigate();

  const [plan, setPlan] = useState<Plan | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [jurisdiction, setJurisdiction] = useState("");
  const [reviewing, setReviewing] = useState(false);
  const [reviewError, setReviewError] = useState<string | null>(null);

  useEffect(() => {
    if (!planId) return;
    getPlan(planId)
      .then(setPlan)
      .catch((err) => setLoadError(apiErrorMessage(err, "Could not load this plan")));
  }, [planId]);

  async function handleReview() {
    if (!planId) return;
    setReviewing(true);
    setReviewError(null);
    try {
      const updated = await triggerReview(planId, jurisdiction || undefined);
      setPlan(updated);
    } catch (err) {
      setReviewError(apiErrorMessage(err, "AI review failed"));
      // Re-fetch since the backend still flips status to 'failed' server-side
      getPlan(planId).then(setPlan).catch(() => {});
    } finally {
      setReviewing(false);
    }
  }

  async function handleDelete() {
    if (!planId || !window.confirm("Delete this plan? This cannot be undone.")) return;
    await deletePlan(planId);
    navigate("/plans");
  }

  if (loadError) return <p className="page form-error">{loadError}</p>;
  if (!plan) return <p className="page page-loading">Loading plan…</p>;

  const notes = plan.ai_review_notes;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>{plan.title}</h1>
          <div className="badge-row">
            <ReviewStatusBadge status={plan.review_status} />
            {notes && <OverallStatusBadge status={notes.overall_status} />}
          </div>
        </div>
        <button type="button" className="btn-ghost btn-danger" onClick={handleDelete}>
          Delete plan
        </button>
      </div>

      {plan.review_status !== "completed" && (
        <div className="card-form review-trigger">
          <label className="field">
            <span>Jurisdiction (optional)</span>
            <input
              value={jurisdiction}
              onChange={(e) => setJurisdiction(e.target.value)}
              placeholder="e.g. City of Springfield — Title 18"
            />
          </label>
          {reviewError && <p className="form-error" role="alert">{reviewError}</p>}
          <button type="button" className="btn-primary" onClick={handleReview} disabled={reviewing}>
            {reviewing ? "Reviewing… this can take up to 30s" : "Run AI review"}
          </button>
        </div>
      )}

      {notes && (
        <div className="review-results">
          <section className="review-summary">
            <h2>Summary</h2>
            <p>{notes.summary}</p>
            <dl className="finding-meta">
              <div>
                <dt>Confidence</dt>
                <dd>{notes.confidence}</dd>
              </div>
              <div>
                <dt>Jurisdiction</dt>
                <dd>{notes.jurisdiction ?? "Not specified"}</dd>
              </div>
              <div>
                <dt>Drawing type</dt>
                <dd>{notes.drawing_metadata?.drawing_type ?? "Not detected"}</dd>
              </div>
              <div>
                <dt>Model</dt>
                <dd>{notes.model}</dd>
              </div>
            </dl>
          </section>

          <section>
            <h2>Findings ({notes.findings.length})</h2>
            {notes.findings.length === 0 ? (
              <p className="hint">No findings — the drawing passed with no noted issues.</p>
            ) : (
              <ul className="findings-list">
                {notes.findings.map((finding) => (
                  <FindingCard key={finding.id} finding={finding} />
                ))}
              </ul>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
