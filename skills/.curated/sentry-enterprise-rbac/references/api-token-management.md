# Api Token Management

## API Token Management

### Create Organization Token

```bash
# Create token with specific scopes
curl -X POST \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CI/CD Token",
    "scopes": ["project:releases", "org:read"]
  }' \
  "https://sentry.io/api/0/organizations/$ORG/api-tokens/"
```

### Token Scopes

```
project:read       - Read project data
project:write      - Modify projects
project:releases   - Create/manage releases
org:read          - Read org data
org:write         - Modify org settings
team:read         - Read team data
team:write        - Manage teams
member:read       - List members
member:write      - Manage members
event:read        - Read events/issues
event:write       - Modify issues
alerts:read       - Read alerts
alerts:write      - Manage alerts
```
