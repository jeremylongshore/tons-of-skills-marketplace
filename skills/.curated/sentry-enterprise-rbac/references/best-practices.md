# Best Practices

## Best Practices

### Principle of Least Privilege

```yaml
# Good: Minimal required access
developer:
  role: member
  teams: [their-team]
  projects: [their-projects]

# Avoid: Over-privileged access
developer:
  role: admin
  teams: [all]
  projects: [all]
```

### Team Organization

```yaml
# Organize by service ownership
teams:
  - name: auth-service
    projects: [auth-api, auth-worker]

  - name: platform
    projects: [all]
    role: read-only

# Not by function (leads to confusion)
teams:
  - name: backend  # Too broad
  - name: frontend # Too broad
```

### Token Hygiene

- Rotate tokens quarterly
- Use specific scopes
- Delete unused tokens
- Audit token usage
