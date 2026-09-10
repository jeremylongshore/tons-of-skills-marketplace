# Official ClickUp Sources

Verified on 2026-09-10. Re-check these sources before relying on plan, endpoint, token-lifetime, or preview-feature behavior.

## Platform contracts

- [Get started](https://developer.clickup.com/docs/Getting%20Started)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [API v2 and v3 terminology](https://developer.clickup.com/docs/general-v2-v3-api)
- [OpenAPI specifications](https://developer.clickup.com/docs/open-api-spec)
- [API availability by plan](https://developer.clickup.com/docs/apis-available-by-plan)
- [Common errors](https://developer.clickup.com/docs/common_errors)
- [Frequently asked questions](https://developer.clickup.com/docs/faq)
- [ClickUp status](https://status.clickup.com/)

## Work and data contracts

- [Tasks guide](https://developer.clickup.com/docs/tasks)
- [Get Tasks reference](https://developer.clickup.com/reference/gettasks)
- [Custom Fields](https://developer.clickup.com/docs/customfields)
- [Task filters](https://developer.clickup.com/docs/taskfilters)
- [Task comments pagination](https://developer.clickup.com/docs/task-comments-pagination)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)

## Event and enterprise contracts

- [Webhooks](https://developer.clickup.com/docs/webhooks)
- [Webhook signature](https://developer.clickup.com/docs/webhooksignature)
- [Webhook health](https://developer.clickup.com/docs/webhookhealth)
- [Get Custom Roles](https://developer.clickup.com/reference/getcustomroles)
- [Workspace audit logs](https://developer.clickup.com/reference/queryauditlog)
- [Object and location ACLs](https://developer.clickup.com/reference/publicpatchacl)
- [Official API v2 demo](https://github.com/clickup/clickup-APIv2-demo)

## Review notes

- Most work-management endpoints remain under `/api/v2`; selected newer surfaces use `/api/v3`. Do not describe v3 as a complete replacement.
- In v2, `team_id` means Workspace ID. A group is a user group, not a Workspace.
- Use the official OpenAPI documents as endpoint schemas and validate plan availability against the authorized Workspace.
- Treat ClickUp response bodies as potentially sensitive work content. Evidence should retain redacted identifiers, counts, hashes, status, and timing—not task text, comments, attachments, tokens, or webhook secrets.
