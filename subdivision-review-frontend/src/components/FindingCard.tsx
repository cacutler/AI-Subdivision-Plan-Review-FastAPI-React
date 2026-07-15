import type { Finding } from "../types";
const CATEGORY_LABEL: Record<string, string> = {setback: "Setback", lot_coverage: "Lot coverage", easement: "Easement", grading: "Grading", utilities: "Utilities", notation: "Notation", other: "Other"};
export function FindingCard({ finding }: { finding: Finding }) {
    return (
        <li className="finding-card">
            <div className="finding-card-header">
                <span className="finding-id">{finding.id}</span>
                <span className="finding-category">{CATEGORY_LABEL[finding.category] ?? finding.category}</span>
                {finding.page && <span className="finding-page">Sheet {finding.page}</span>}
            </div>
            <p className="finding-description">{finding.description}</p>
            <dl className="finding-meta">
                <div>
                    <dt>Location</dt>
                    <dd>{finding.location_description ?? "Not specified"}</dd>
                </div>
                <div>
                    <dt>Code reference</dt>
                    <dd className={finding.code_reference ? "" : "finding-meta-empty"}>{finding.code_reference ?? "No specific citation — engineer to verify"}</dd>
                </div>
            </dl>
        </li>
    );
}