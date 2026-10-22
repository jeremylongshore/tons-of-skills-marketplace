---
name: responding-to-security-incidents
description: 'Analyze and guide security incident response, investigation, and remediation
  processes.

  Use when you need to handle security breaches, classify incidents, develop response
  playbooks, gather forensic evidence, or coordinate remediation efforts.

  Trigger with phrases like "security incident response", "ransomware attack response",
  "data breach investigation", "incident playbook", or "security forensics".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(log-analysis:*), Bash(forensics:*),
  Bash(network-trace:*)
version: 1.33.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- security
- incident-response
- responding-security
compatibility: Designed for Claude Code
---
# Responding To Security Incidents

## Overview

Guide the full NIST SP 800-61 incident response lifecycle: detection, containment, eradication, recovery, and post-incident analysis. Classify incidents by type (ransomware, data breach, DDoS, credential compromise, insider threat) and severity, then coordinate evidence preservation, threat containment, and root-cause investigation.

## Prerequisites

- System and application logs accessible in `${CLAUDE_SKILL_DIR}/logs/` (auth logs, web server logs, database access logs)
- Network traffic captures (PCAP) or SIEM alert exports available
- Incident response team contact information and escalation paths documented
- Backup systems operational and recovery procedures tested
- Write permissions for incident documentation in `${CLAUDE_SKILL_DIR}/incidents/`
- Forensic tools available: Volatility (memory), Autopsy/FTK Imager (disk), tcpdump/Wireshark (network)

## Instructions

1. **Classify the incident**: determine type (ransomware, data breach, DDoS, phishing, insider threat), assign severity (Critical/High/Medium/Low), and record initial detection timestamp and method.
2. **Scope affected systems**: identify all compromised hosts, user accounts, data stores, and network segments. Map the blast radius.
3. **Preserve evidence before any changes**: capture memory dumps (`volatility -f memdump.raw imageinfo`), create disk images, export running process lists (`ps auxf`), and snapshot network connection state (`ss -tulnp`).
4. **Collect log evidence**: gather authentication logs (successful and failed), application error logs, firewall/IDS alerts, DNS query logs, and proxy server logs. Store originals in `${CLAUDE_SKILL_DIR}/incidents/evidence/`.
5. **Contain the threat**: isolate affected systems from the network, disable compromised accounts, block malicious IPs at the firewall, and revoke compromised API keys or tokens.
6. **Investigate and reconstruct timeline**: identify initial access vector, map lateral movement, determine data exfiltration scope, locate persistence mechanisms (cron jobs, startup scripts, web shells), and document all IOCs (IPs, hashes, domains, file paths).
7. **Eradicate the threat**: remove malware and backdoors, patch exploited vulnerabilities, reset all potentially compromised credentials, and update firewall rules.
8. **Recover operations**: restore from verified clean backups, rebuild compromised systems from hardened images, validate system integrity, and monitor for reinfection with heightened alerting.
9. **Document the incident**: produce a comprehensive report at `${CLAUDE_SKILL_DIR}/incidents/incident-YYYYMMDD-HHMM.md` containing executive summary, detailed timeline, root cause analysis, IOC list, and lessons learned.
10. **Create remediation backlog**: list all follow-up actions (patch gaps, monitoring improvements, policy changes) with owners and deadlines.

See [`references/implementation.md`](references/implementation.md) for the seven-phase implementation workflow.

## Output

- **Incident Report**: `${CLAUDE_SKILL_DIR}/incidents/incident-YYYYMMDD-HHMM.md` with timeline, root cause, IOCs, and impact assessment
- **IOC List**: machine-readable indicators (IP addresses, file hashes, domains, YARA rules)
- **After-Action Review**: lessons learned, process gaps, and recommended improvements
- **Remediation Backlog**: prioritized follow-up tasks with owners and deadlines

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Critical logs missing from `${CLAUDE_SKILL_DIR}/logs/` | Log rotation, deletion, or attacker tampering | Work with available data; note gaps; improve logging retention for future incidents |
| System state modified before evidence collection | First responder made changes before forensic capture | Document contamination; collect remaining evidence; prioritize network and SIEM logs |
| Attacker still has active access during investigation | Ongoing compromise detected | Prioritize containment over investigation; implement emergency network isolation |
| Permission denied accessing system memory | Insufficient forensic tool privileges | Escalate to obtain root/admin access; fall back to available log and network data |
| Backups encrypted or corrupted by ransomware | Attacker targeted backup infrastructure | Identify offline/air-gapped backups; assess rebuild-from-scratch feasibility |

## Examples

- "Credential stuffing detected. Use logs in `${CLAUDE_SKILL_DIR}/logs/` to triage the incident, scope affected accounts, and propose containment steps."
- "Create an incident response plan for a suspected data breach: list evidence to collect, containment actions, and notification requirements."
- "Investigate a web shell found at `/var/www/html/uploads/cmd.php`. Trace the initial access vector, identify persistence mechanisms, and produce an IOC list."

## Resources

- NIST SP 800-61r2 Computer Security Incident Handling Guide: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf
- SANS Incident Handler's Handbook: https://www.sans.org/white-papers/33901/
- CISA Incident Response Guide:
- Volatility Framework (memory forensics): https://www.volatilityfoundation.org/
- Autopsy (disk forensics): https://www.autopsy.com/
- [`references/errors.md`](references/errors.md) -- full error handling reference
- [`references/examples.md`](references/examples.md) -- additional usage examples
- https://intentsolutions.io
