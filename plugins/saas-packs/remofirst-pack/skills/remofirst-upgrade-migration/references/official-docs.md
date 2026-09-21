# RemoFirst cutover evidence

Reviewed: 2026-09-12

## Primary sources

- [Workday connector guide](https://knowledgebase.remofirst.com/hc/en-us/articles/53164120410644-Workday-RemoFirst-Integration-Client-Guide) — one-way direction, mapping, manual sync, supported states, time conversion, and offboarding confirmation.
- [ADP connector guide](https://knowledgebase.remofirst.com/hc/en-us/articles/39824562179348-ADP-Workforce-Now-Connecting-to-RemoFirst) — connector activation and SSO authorization.
- [Downloadable reports](https://knowledgebase.remofirst.com/hc/en-us/articles/34884776744468-A-Comprehensive-Guide-to-Downloadable-Reports-on-the-Remofirst-Platform) — controlled export alternatives and reconciliation surfaces.
- [Contractor timesheets](https://knowledgebase.remofirst.com/hc/en-us/articles/49864322520468-How-to-Manage-and-Approve-Contractor-Timesheets) — documented CSV format and locked approval state.
- [Payroll management](https://knowledgebase.remofirst.com/hc/en-us/articles/34907211691924-Payroll-management-and-invoice-generation-on-the-platform) — the production boundary that post-cutover reconciliation must protect.
- [DPA guidance](https://knowledgebase.remofirst.com/hc/en-us/articles/49855444391828-Ensuring-GDPR-Compliance-Your-Data-Protection-Agreement-DPA-with-RemoFirst-Talent) — privacy review for changed data flows.
- [Support channels](https://knowledgebase.remofirst.com/hc/en-us/articles/40237072233236-How-do-I-contact-RemoFirst-for-support) — escalation and cutover support path.

## Contract notes

The safe migration unit is a documented workflow or connector boundary, not a
generic API version. Parallel reconciliation, one authoritative writer, explicit
human approvals, and a controlled fallback protect payroll and worker records.
