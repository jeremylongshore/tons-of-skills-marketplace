# TechSmith Operator Skill Pack

> 18 source-grounded Claude Code skills for controlled Snagit and Camtasia desktop operations.

## What This Is

This pack covers supported Snagit COM automation, current Camtasia recorder and modern export boundaries, managed desktop deployment, licensing, local media handling, observability, and safe artifact promotion. It is built for operator workflows, not a fictional TechSmith web API.

The pack deliberately version-gates historical surfaces:

- Snagit COM remains supported on Windows and is grounded in TechSmith's current 2025 COM guide and official samples.
- Current Snagit image inputs are desktop `0`, window `1`, and region `4`; outputs are file `2` and clipboard `4`.
- Snagit `Capture()` is asynchronous and requires completion plus result validation.
- Camtasia 2022 and later use `CamtasiaRecorder.exe` for documented recorder control.
- The legacy Camtasia exporter was removed in 2024.1.3; current workflows do not prescribe `CamtasiaProducer.exe`.
- Active Camtasia projects and media remain on local, non-synced storage until Camtasia closes.

## Installation

```bash
/plugin install techsmith-pack@claude-code-plugins-plus
```

## Skills

| Skill | Operator outcome |
|---|---|
| `techsmith-install-auth` | Select and verify install, license, activation, connectivity, and COM registration |
| `techsmith-hello-world` | Prove Snagit COM safely without capturing by default |
| `techsmith-local-dev-loop` | Iterate with fakes, official samples, and bounded live probes |
| `techsmith-sdk-patterns` | Isolate Snagit behind a typed, deadline-bound COM adapter |
| `techsmith-core-workflow-a` | Run a controlled Snagit image capture with exact enums and output checks |
| `techsmith-core-workflow-b` | Produce a version-pinned Camtasia batch through the modern exporter |
| `techsmith-common-errors` | Classify registration, command, storage, media, export, and activation failures |
| `techsmith-debug-bundle` | Build a redacted, reviewed support evidence bundle |
| `techsmith-rate-limits` | Apply honest desktop capacity and queue guardrails |
| `techsmith-security-basics` | Enforce capture consent, license secrecy, path, sharing, and retention controls |
| `techsmith-prod-checklist` | Issue an evidence-backed production go/no-go decision |
| `techsmith-upgrade-migration` | Upgrade applications and migrate legacy content without overwriting originals |
| `techsmith-ci-integration` | Split secretless contract CI from protected licensed workstation smoke tests |
| `techsmith-deploy-integration` | Build and roll out reviewed MSI/MST or macOS deployment artifacts |
| `techsmith-webhooks-events` | Turn COM and filesystem signals into durable local artifact events |
| `techsmith-performance-tuning` | Tune measured workstation and export bottlenecks safely |
| `techsmith-cost-tuning` | Optimize entitlements, worker utilization, rework, storage, and retention |
| `techsmith-reference-architecture` | Design a controlled desktop worker and artifact-promotion topology |

## Primary Sources

- [Snagit 2025 COM Server Guide](https://assets.techsmith.com/Docs/Snagit-2025-COM-Server-Guide.pdf)
- [Official Snagit COM samples](https://github.com/TechSmith/Snagit-COM-Samples)
- [Camtasia recorder command line](https://support.techsmith.com/hc/en-us/articles/203728678-Using-Command-Lines-to-Operate-the-Camtasia-Recorder)
- [Legacy exporter removal](https://support.techsmith.com/hc/en-us/articles/31882425655565-Removal-of-Legacy-Exporter-From-Camtasia-2024)
- [Deploying TechSmith products](https://support.techsmith.com/hc/en-us/articles/43771074923021-Deploying-TechSmith-Products)

## License

MIT
