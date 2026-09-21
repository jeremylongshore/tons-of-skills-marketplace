# RemoFirst security-baseline evidence

Reviewed: 2026-09-12

## Primary sources

- [Client two-factor authentication](https://knowledgebase.remofirst.com/hc/en-us/articles/34910927256340-Securing-your-Remofirst-Account-with-2FA-Two-Factor-Authentication-for-Clients) — authenticator setup, login, recovery-code use, and disable flow.
- [Manager access groups](https://knowledgebase.remofirst.com/hc/en-us/articles/34711781448340-Managing-access-rights-with-groups) — group permissions and the no-group Superuser default.
- [Direct-manager assignment](https://knowledgebase.remofirst.com/hc/en-us/articles/37526157891988-Assigning-a-Direct-Manager-to-Your-Employees) — workforce reporting scope distinct from application groups.
- [Downloadable reports](https://knowledgebase.remofirst.com/hc/en-us/articles/34884776744468-A-Comprehensive-Guide-to-Downloadable-Reports-on-the-Remofirst-Platform) — payroll, invoice, time-off, and workforce export surfaces.
- [Workday connector guide](https://knowledgebase.remofirst.com/hc/en-us/articles/53164120410644-Workday-RemoFirst-Integration-Client-Guide) — Workday integration identity and OAuth credentials.
- [DPA guidance](https://knowledgebase.remofirst.com/hc/en-us/articles/49855444391828-Ensuring-GDPR-Compliance-Your-Data-Protection-Agreement-DPA-with-RemoFirst-Talent) — GDPR and data-processing agreement workflow.
- [Support channels](https://knowledgebase.remofirst.com/hc/en-us/articles/40237072233236-How-do-I-contact-RemoFirst-for-support) — approved escalation paths.

## Contract notes

This baseline treats unassigned groups as elevated access, recovery and connector
material as secrets, and exports as sensitive. It records control evidence rather
than credentials, recovery codes, worker documents, bank data, or payroll rows.
