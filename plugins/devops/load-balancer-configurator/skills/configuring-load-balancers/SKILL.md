---
name: configuring-load-balancers
description: 'Configure use when configuring load balancers including ALB, NLB, Nginx,
  and HAProxy. Trigger with phrases like "configure load balancer", "create ALB",
  "setup nginx load balancing", or "haproxy configuration". Generates production-ready
  configurations with health checks, SSL termination, sticky sessions, and traffic
  distribution rules.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(aws:*), Bash(gcloud:*), Bash(nginx:*)
version: 1.29.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- devops
- load-balancers
compatibility: Designed for Claude Code
---
# Configuring Load Balancers

## Overview

Configure load balancers across AWS (ALB, NLB), GCP (HTTP(S) LB, TCP/UDP LB), Nginx, and HAProxy. Generate production-ready configurations with health checks, SSL/TLS termination, path-based and host-based routing, sticky sessions, rate limiting, and traffic distribution rules for high-availability deployments.

## Prerequisites

- Backend servers identified with IPs, DNS names, and ports
- Load balancer type determined: L4 (NLB, HAProxy TCP) or L7 (ALB, Nginx, HAProxy HTTP)
- SSL/TLS certificates available (ACM, Let's Encrypt, or self-signed) if using HTTPS
- Health check endpoints defined on backend services (e.g., `/health` returning 200)
- Cloud provider CLI installed for managed load balancers (`aws`, `gcloud`)

## Instructions

1. Select load balancer type based on requirements: ALB for HTTP/HTTPS with path routing, NLB for TCP/UDP with static IPs, Nginx for on-prem reverse proxy, HAProxy for high-performance TCP/HTTP
2. Define the backend pool: list all backend server addresses, ports, and weights for weighted distribution
3. Configure health checks with appropriate interval (10-30s), timeout (5s), healthy threshold (3), and unhealthy threshold (2)
4. Set up SSL/TLS termination: configure certificates, redirect HTTP to HTTPS, set minimum TLS version to 1.2
5. Define routing rules: path-based routing (`/api` -> API pool, `/static` -> CDN), host-based routing (`api.example.com` -> API)
6. Enable session persistence (sticky sessions) using cookies or source IP affinity where needed for stateful applications
7. Add connection draining to gracefully handle backend removal during deployments
8. Configure logging and monitoring: access logs to S3/CloudWatch, request metrics, error rate dashboards
9. Test the configuration: validate syntax (`nginx -t`, HAProxy config check), verify traffic distribution, and confirm failover behavior

## Output

- Nginx configuration files (`nginx.conf`, site configs) with upstream blocks and server directives
- HAProxy configuration (`haproxy.cfg`) with frontend/backend sections
- Terraform HCL for AWS ALB/NLB with target groups, listeners, and rules
- GCP load balancer Terraform with backend services, URL maps, and health checks
- SSL certificate configuration and renewal automation

## Error Handling

| Error | Cause | Solution |
|-------|-------|---------|
| `502 Bad Gateway` | Backend server unreachable or not responding | Verify backend IPs, ports, and firewall rules; check backend service health |
| `SSL certificate verify failed` | Certificate expired, wrong chain, or key mismatch | Verify certificate validity and chain with `openssl s_client`; regenerate if needed |
| `Target is unhealthy` | Health check endpoint returning non-200 or timing out | Verify health check path returns 200; increase timeout if backend is slow to respond |
| `nginx: configuration file test failed` | Syntax error in Nginx configuration | Run `nginx -t` to identify the specific error line; fix syntax and test again |
| `Session persistence not working` | Cookie-based stickiness misconfigured or client not sending cookies | Verify cookie name matches; use IP-based affinity as fallback for non-browser clients |

## Examples

- "Configure an AWS ALB with HTTPS listener, path-based routing to two target groups (/api and /web), and health checks on /health."
- "Generate an Nginx reverse proxy config with upstream servers, sticky sessions via cookie, and rate limiting at 100 req/s per IP."
- "Create a HAProxy configuration for TCP load balancing across 4 database read replicas with health checks and connection draining."

## Resources

- Nginx load balancing: https://nginx.org/en/docs/http/load_balancing.html
- HAProxy configuration: https://www.haproxy.org/download/2.8/doc/configuration.txt
- AWS ALB: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/
- GCP Load Balancing: https://cloud.google.com/load-balancing/docs
- See [`references/errors.md`](references/errors.md) for additional error handling patterns
