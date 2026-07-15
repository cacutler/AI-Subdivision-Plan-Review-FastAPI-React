import { useState, type SubmitEvent } from "react";
import { useNavigate } from "react-router-dom";
import { uploadPlan } from "../api/plans";
import { apiErrorMessage } from "../api/client";
export function UploadPlanPage() {
    const navigate = useNavigate();
    const [title, setTitle] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);
    async function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
        e.preventDefault();
        if (!file) {
            setError("Choose a PDF file to upload");
            return;
        }
        setError(null);
        setSubmitting(true);
        try {
            const plan = await uploadPlan(title, file);
            navigate(`/plans/${plan.id}`);
        } catch (err) {
            setError(apiErrorMessage(err, "Upload failed"));
        } finally {
            setSubmitting(false);
        }
    }
    return (
        <div className="page page-narrow">
            <h1>Upload plan</h1>
            <form className="card-form" onSubmit={handleSubmit}>
                <label className="field">
                    <span>Title</span>
                    <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. 1420 Maple St — Grading Plan" required/>
                </label>
                <label className="field">
                    <span>PDF file</span>
                    <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files?.[0] ?? null)} required/>
                </label>
                {error && <p className="form-error" role="alert">{error}</p>}
                <button type="submit" className="btn-primary" disabled={submitting}>{submitting ? "Uploading…" : "Upload"}</button>
            </form>
            <p className="hint">After uploading, open the plan to trigger the AI compliance review.</p>
        </div>
    );
}