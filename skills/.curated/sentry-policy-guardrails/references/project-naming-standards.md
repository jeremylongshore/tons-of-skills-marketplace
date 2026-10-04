# Project Naming Standards

## Project Naming Standards

### Enforced Naming Convention

```typescript
// Project naming: {team}-{service}-{environment}
// Examples: payments-api-production, auth-worker-staging

function validateProjectName(name: string): boolean {
  const pattern = /^[a-z]+-[a-z]+-(?:production|staging|development)$/;
  return pattern.test(name);
}

// API to create project with validation
async function createProject(
  teamSlug: string,
  serviceName: string,
  environment: string
): Promise<void> {
  const projectName = `${teamSlug}-${serviceName}-${environment}`;

  if (!validateProjectName(projectName)) {
    throw new Error(
      `Invalid project name: ${projectName}. ` +
      'Must follow pattern: {team}-{service}-{environment}'
    );
  }

  // Create via Sentry API
  await fetch(`https://sentry.io/api/0/teams/${ORG}/${teamSlug}/projects/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${SENTRY_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name: projectName }),
  });
}
```
