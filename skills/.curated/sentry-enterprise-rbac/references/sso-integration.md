# Sso Integration

## SSO Integration

### SAML Configuration

1. Settings → Auth → Configure SAML
2. Copy ACS URL and Entity ID to IdP
3. Upload IdP metadata or configure manually:
   - IdP Entity ID
   - SSO URL
   - Certificate

### SAML Attribute Mapping

```xml
<!-- Required attributes -->
<Attribute Name="email" />

<!-- Optional attributes -->
<Attribute Name="firstName" />
<Attribute Name="lastName" />
<Attribute Name="teams" />  <!-- For auto team assignment -->
```

### SCIM Provisioning

```bash
# Enable SCIM
# Settings → Auth → SCIM

# SCIM endpoint
https://sentry.io/api/0/organizations/$ORG/scim/v2/

# Supported resources
- Users
- Groups (Teams)
```

### Auto Team Assignment

```json
// IdP sends team membership
{
  "teams": ["backend", "frontend"],
  "role": "member"
}
```
