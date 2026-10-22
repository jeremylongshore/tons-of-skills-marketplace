---
name: creating-kubernetes-deployments
description: 'Deploy applications to Kubernetes with production-ready manifests.

  Supports Deployments, Services, Ingress, HPA, ConfigMaps, Secrets, StatefulSets,
  and NetworkPolicies.

  Includes health checks, resource limits, auto-scaling, and TLS termination. Use
  when working with creating kubernetes deployments. Trigger with ''creating'', ''kubernetes'',
  ''deployments''.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(kubectl:*)
version: 1.29.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- devops
- deployment
- kubernetes
- scaling
compatibility: Designed for Claude Code
---
# Creating Kubernetes Deployments

Generate production-ready Kubernetes manifests with health checks, resource limits, and security best practices.

## Quick Start

### Basic Deployment + Service

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-api
  labels:
    app: my-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
  template:
    metadata:
      labels:
        app: my-api
    spec:
      containers:
      - name: my-api
        image: my-registry/my-api:v1.0.0
        ports:
        - containerPort: 8080  # 8080: HTTP proxy port
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080  # HTTP proxy port
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8080  # HTTP proxy port
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: my-api
spec:
  type: ClusterIP
  selector:
    app: my-api
  ports:
  - port: 80
    targetPort: 8080  # HTTP proxy port
```

## Deployment Strategies

| Strategy | Use Case | Configuration |
|----------|----------|---------------|
| RollingUpdate | Zero-downtime updates | `maxSurge: 25%`, `maxUnavailable: 25%` |
| Recreate | Stateful apps, incompatible versions | `type: Recreate` |
| Blue-Green | Instant rollback | Two deployments, switch Service selector |
| Canary | Gradual rollout | Multiple deployments with weighted traffic |

### Blue-Green Deployment

```yaml
# Blue deployment (current production)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-api-blue
  labels:
    app: my-api
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-api
      version: blue
  template:
    metadata:
      labels:
        app: my-api
        version: blue
    spec:
      containers:
      - name: my-api
        image: my-registry/my-api:v1.0.0
---
# Service points to blue
apiVersion: v1
kind: Service
metadata:
  name: my-api
spec:
  selector:
    app: my-api
    version: blue  # Switch to 'green' for deployment
  ports:
  - port: 80
    targetPort: 8080  # 8080: HTTP proxy port
```

## Service Types

| Type | Use Case | Access |
|------|----------|--------|
| ClusterIP | Internal services | `my-api.namespace.svc.cluster.local` |
| NodePort | Development, debugging | `<NodeIP>:<NodePort>` |
| LoadBalancer | External traffic (cloud) | Cloud provider LB IP |
| ExternalName | External service proxy | DNS CNAME |

## Ingress with TLS

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-api-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: api-tls-secret
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-api
            port:
              number: 80
```

## Resource Limits

**Always set resource requests and limits:**

```yaml
resources:
  requests:    # Guaranteed resources
    cpu: 100m  # 0.1 CPU core
    memory: 256Mi
  limits:      # Maximum allowed
    cpu: 500m  # 0.5 CPU core
    memory: 512Mi
```

| Workload Type | CPU Request | Memory Request | CPU Limit | Memory Limit |
|---------------|-------------|----------------|-----------|--------------|
| Web API | 100m-500m | 256Mi-512Mi | 500m-1000m | 512Mi-1Gi |
| Worker | 250m-1000m | 512Mi-1Gi | 1000m-2000m | 1Gi-2Gi |
| Database | 500m-2000m | 1Gi-4Gi | 2000m-4000m | 4Gi-8Gi |

## Health Checks

### Liveness Probe (Is container running?)

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080  # 8080: HTTP proxy port
  initialDelaySeconds: 30  # Wait for app startup
  periodSeconds: 10         # Check every 10s
  timeoutSeconds: 5         # Timeout per check
  failureThreshold: 3       # Restart after 3 failures
```

### Readiness Probe (Ready for traffic?)

```yaml
readinessProbe:
  httpGet:
    path: /readyz
    port: 8080  # 8080: HTTP proxy port
  initialDelaySeconds: 5    # Quick check after start
  periodSeconds: 5          # Check every 5s
  successThreshold: 1       # 1 success = ready
  failureThreshold: 3       # Remove from LB after 3 failures
```

### Startup Probe (Slow-starting apps)

```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: 8080  # 8080: HTTP proxy port
  initialDelaySeconds: 0
  periodSeconds: 10
  failureThreshold: 30      # Allow 5 minutes to start (30 * 10s)
```

## Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 300: Wait 5min before scale down
```

## ConfigMaps and Secrets

### ConfigMap (Non-sensitive config)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-api-config
data:
  LOG_LEVEL: "info"
  API_ENDPOINT: "https://api.example.com"
  config.yaml: |
    server:
      port: 8080  # 8080: HTTP proxy port
    features:
      enabled: true
```

### Secret (Sensitive data - base64 encoded)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-api-secrets
type: Opaque
data:
  API_KEY: YXBpLWtleS1oZXJl          # echo -n "api-key-here" | base64
  DATABASE_URL: cG9zdGdyZXM6Ly8uLi4=  # echo -n "postgres://..." | base64
```

### Using in Deployment

```yaml
spec:
  containers:
  - name: my-api
    envFrom:
    - configMapRef:
        name: my-api-config
    - secretRef:
        name: my-api-secrets
    volumeMounts:
    - name: config-volume
      mountPath: /app/config
  volumes:
  - name: config-volume
    configMap:
      name: my-api-config
```

## Instructions

1. **Gather Requirements**
   - Application name, container image, port
   - Replica count and resource requirements
   - Health check endpoints
   - External access requirements (Ingress/LoadBalancer)

2. **Generate Base Manifests**
   - Create Deployment with resource limits and probes
   - Create Service (ClusterIP for internal, LoadBalancer for external)
   - Add ConfigMap for configuration
   - Add Secret for sensitive data

3. **Add Production Features**
   - Configure Ingress with TLS if external access needed
   - Add HPA for auto-scaling
   - Add NetworkPolicy for security
   - Add PodDisruptionBudget for availability

4. **Validate and Apply**

   ```bash
   # Validate manifests
   kubectl apply -f manifests/ --dry-run=server

   # Apply to cluster
   kubectl apply -f manifests/

   # Watch rollout
   kubectl rollout status deployment/my-api
   ```

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive troubleshooting.

| Error | Quick Fix |
|-------|-----------|
| ImagePullBackOff | Check image name, tag, registry credentials |
| CrashLoopBackOff | Check logs: `kubectl logs <pod>` |
| OOMKilled | Increase memory limits |
| Pending | Check resources: `kubectl describe pod <pod>` |

## Examples

See [`references/examples.md`](references/examples.md) for detailed walkthroughs.

## Resources

- Kubernetes documentation: https://kubernetes.io/docs/
- kubectl reference: https://kubernetes.io/docs/reference/kubectl/
- Templates in `${CLAUDE_SKILL_DIR}/assets/`
- Scripts in `${CLAUDE_SKILL_DIR}/scripts/`

## Overview

Deploy applications to Kubernetes with production-ready manifests.

## Prerequisites

- Access to the Kubernetes environment or API
- Required CLI tools installed and authenticated
- Familiarity with Kubernetes concepts and terminology

## Output

- Configuration files or code changes applied to the project
- Validation report confirming correct implementation
- Summary of changes made and their rationale

See Kubernetes implementation details for output format specifications.
