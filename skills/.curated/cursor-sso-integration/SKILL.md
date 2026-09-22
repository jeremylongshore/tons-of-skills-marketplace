---
name: cursor-sso-integration
description: 'Configure SAML 2.0 and OIDC SSO for Cursor with Okta, Microsoft Entra
  ID, and Google Workspace.

  Triggers on "cursor sso", "cursor saml", "cursor oauth", "enterprise cursor auth",
  "cursor okta",

  "cursor entra", "cursor scim".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- authentication
compatibility: Designed for Claude Code
---
# Cursor SSO Integration

## Overview

Integrate Cursor with the organization's identity provider through a phased, auditable SSO/SCIM rollout that preserves emergency recovery and least privilege.

## Instructions

1. Obtain approved SAML/SCIM values from the identity owner and validate them in a non-production or pilot tenant.
2. Pilot with a limited group, monitor sign-in/provisioning results, and correct attribute/group mappings before enforcement.
3. Enable organization-wide enforcement only after rollback/emergency access and deprovisioning paths are tested.
4. Retain redacted setup evidence and schedule access-review verification through the IdP.

## Output

- An audited SSO configuration with scoped role mappings, tested SCIM provisioning, and a documented rollback/emergency-access path.

## Examples

Pilot a single IdP group, confirm a new member receives the least-privilege Cursor role and a departed member is deprovisioned, then document the redacted IdP/Cursor audit evidence. If mapping is wrong, disable pilot enforcement and correct the group claim before organization-wide rollout.

Configure Single Sign-On for Cursor using SAML 2.0 or OIDC. Available on Business and Enterprise plans. Supports Okta, Microsoft Entra ID (Azure AD), Google Workspace, and any SAML 2.0 / OIDC compliant IdP.

## Prerequisites

- Cursor Business or Enterprise subscription
- Admin access to both Cursor organization and Identity Provider
- Verified company domain in Cursor admin dashboard
- Understanding of SAML 2.0 or OIDC concepts

## SSO Configuration: Okta

### Step 1: Create SAML Application in Okta

1. Okta Admin Console > Applications > Create App Integration
2. Select **SAML 2.0**
3. App name: "Cursor IDE"

### Step 2: Configure SAML Settings

```
Single Sign-On URL (ACS URL):
  https://cursor.com/api/auth/saml/callback

Audience URI (Entity ID):
  https://cursor.com/api/auth/saml

Name ID format: EmailAddress
Application username: Email

Attribute Statements:
  email    → user.email       (Required)
  name     → user.firstName + " " + user.lastName  (Optional)
```

### Step 3: Download IdP Metadata

After creating the app in Okta:

1. Go to the app's "Sign On" tab
2. Click "Identity Provider metadata" link
3. Save the XML file

### Step 4: Upload to Cursor

1. Cursor Admin Dashboard > SSO
2. Select "SAML 2.0"
3. Upload the IdP metadata XML (or paste the metadata URL)
4. Save configuration

### Step 5: Test

1. Open Cursor incognito
2. Sign in with your `@company.com` email
3. Should redirect to Okta login
4. After auth, return to Cursor authenticated

## SSO Configuration: Microsoft Entra ID

### Step 1: Register Enterprise Application

1. Azure Portal > Entra ID > Enterprise applications > New application
2. Create your own application > "Cursor IDE"
3. Select "Integrate any other application you don't find in the gallery (Non-gallery)"

### Step 2: Configure SAML

In the enterprise app > Single sign-on > SAML:

```
Basic SAML Configuration:
  Identifier (Entity ID):     https://cursor.com/api/auth/saml
  Reply URL (ACS URL):        https://cursor.com/api/auth/saml/callback
  Sign-on URL:                https://cursor.com

Attributes & Claims:
  Unique User Identifier:     user.mail
  email:                      user.mail
  name:                       user.displayname
```

### Step 3: Download Federation Metadata XML

In Entra ID app > SAML Signing Certificate > Download "Federation Metadata XML"

### Step 4: Upload to Cursor

Same as Okta Step 4: Admin Dashboard > SSO > Upload metadata.

## SSO Configuration: Google Workspace

### Step 1: Create SAML App

1. Google Admin Console > Apps > Web and mobile apps > Add app > Add custom SAML app
2. App name: "Cursor IDE"

### Step 2: Configure

```
ACS URL:        https://cursor.com/api/auth/saml/callback
Entity ID:      https://cursor.com/api/auth/saml
Name ID format: EMAIL
Name ID:        Basic Information > Primary email
```

### Step 3: Download IdP Metadata

Google provides this during app creation. Save the metadata XML.

### Step 4: Upload to Cursor

Admin Dashboard > SSO > Upload metadata.

## SCIM Provisioning (Enterprise Only)

SCIM 2.0 automatically syncs users and groups from your IdP to Cursor:

### What SCIM Handles

| Operation | Trigger | Cursor Action |
|-----------|---------|---------------|
| User created in IdP | Okta/Entra creates user | Seat assigned in Cursor |
| User deactivated in IdP | Okta/Entra deactivates | Seat revoked in Cursor |
| Group membership change | User added/removed from group | Role updated in Cursor |

### SCIM Setup (Okta Example)

1. Cursor Admin Dashboard > SCIM > Generate SCIM token
2. In Okta > Cursor app > Provisioning > Enable SCIM
3. Configure:

   ```
   SCIM connector base URL: https://cursor.com/api/scim/v2
   Unique identifier field: email
   Authentication mode: Bearer token
   Bearer token: [paste token from Cursor]
   ```

4. Enable: Create Users, Deactivate Users, Push Groups

## Domain Verification

Required before SSO activation:

1. Cursor Admin Dashboard > Domains > Add domain
2. Add DNS TXT record:

   ```
   Type:  TXT
   Host:  _cursor-verification
   Value: cursor-verify=xxxxxxxxxxxxxxxxxxxx
   ```

3. Wait for DNS propagation (up to 48 hours, usually minutes)
4. Click "Verify" in Cursor admin

## Rollout Strategy

### Phase 1: Pilot (1 week)

```
[ ] Configure SSO with test users only
[ ] Verify sign-in flow works end-to-end
[ ] Test: new user SSO sign-in creates Cursor account
[ ] Test: sign-out and re-sign-in preserves settings
[ ] Test: IdP session timeout triggers re-auth in Cursor
[ ] Document any issues or friction points
```

### Phase 2: Gradual Rollout (2 weeks)

```
[ ] Enable SSO for one team/department
[ ] Monitor sign-in success rate in admin dashboard
[ ] Collect feedback on the auth experience
[ ] Resolve any IdP attribute mapping issues
```

### Phase 3: Organization-Wide

```
[ ] Enable SSO requirement for all users
[ ] Disable password-based login (optional)
[ ] Enable SCIM for automatic provisioning
[ ] Set up IdP group → Cursor role mapping
[ ] Document SSO in company IT wiki
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| "SAML Response Invalid" | Wrong ACS URL or Entity ID | Verify URLs match exactly |
| User not created after SSO | SCIM not enabled or email mismatch | Check SCIM logs in IdP |
| "Domain not verified" | DNS record not propagated | Wait, then re-verify |
| Redirect loop after SSO | Browser cookies corrupted | Clear cookies for cursor.com |
| SSO works but wrong role | Group mapping misconfigured | Check IdP group assignments |
| "No seat available" | All seats assigned | Purchase more seats or revoke unused |

## Enterprise Considerations

- **MFA enforcement**: Apply MFA policy at the IdP level (Okta/Entra). Cursor defers to IdP for MFA.
- **Session timeout**: Configure session lifetime in IdP. Cursor respects IdP session expiry.
- **Emergency access**: Keep one admin account with email/password login in case SSO is misconfigured
- **Compliance**: SSO provides centralized access logging at the IdP level for audit trails
- **Cost**: SSO is included in Business ($40/user/mo) and Enterprise plans. No additional SSO fee.

## Resources

- [Cursor SSO Documentation](https://docs.cursor.com/plans/business/sso)
- [Cursor Enterprise](https://cursor.com/enterprise)
- [SAML 2.0 Specification](https://docs.oasis-open.org/security/saml/v2.0/)
- [Okta SAML Guide](https://developer.okta.com/docs/guides/saml-application-setup/)
