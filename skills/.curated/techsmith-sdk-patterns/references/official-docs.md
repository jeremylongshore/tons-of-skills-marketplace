# TechSmith Official Documentation Snapshot

Verified against primary TechSmith documentation on 2026-09-10. Product support pages and the installed version's documentation remain authoritative; recheck them before changing deployment, licensing, or destructive migration behavior.

## Snagit automation

- [Snagit 2025 COM Server Guide](https://assets.techsmith.com/Docs/Snagit-2025-COM-Server-Guide.pdf)
- [Official Snagit COM samples](https://github.com/TechSmith/Snagit-COM-Samples)
- [Snagit 2025 Deployment Tool Guide](https://assets.techsmith.com/Docs/Snagit-2025-Deployment-Tool-Guide.pdf)
- [Customize the Snagit MSI with an MST](https://support.techsmith.com/hc/en-us/articles/203730778-Customize-the-Snagit-installer-MSI-with-Transform-MST-for-Enterprise-Installation)
- [Install Snagit with MSI](https://support.techsmith.com/hc/en-us/articles/203731128-Installing-Snagit-with-MSI-Installer)
- [Enterprise Snagit installation on macOS](https://support.techsmith.com/hc/en-us/articles/115007344888-Enterprise-Install-Guidelines-for-Snagit-on-MacOS)
- [Export a Snagit library](https://support.techsmith.com/hc/en-us/articles/27142747345805-How-Do-I-Export-My-Snagit-Library-if-I-No-Longer-Plan-to-Use-Snagit)

## Camtasia operations

- [Camtasia recorder command line](https://support.techsmith.com/hc/en-us/articles/203728678-Using-Command-Lines-to-Operate-the-Camtasia-Recorder)
- [Camtasia 2025 Deployment Tool Guide](https://assets.techsmith.com/docs/Camtasia_2025_Deployment_Tool_Guide.pdf)
- [Legacy exporter removal](https://support.techsmith.com/hc/en-us/articles/31882425655565-Removal-of-Legacy-Exporter-From-Camtasia-2024)
- [TSCPROJ and TREC file handling](https://support.techsmith.com/hc/en-us/articles/203730028-Working-with-Camtasia-Editor-TSCPROJ-and-TREC-Files)
- [Share a Camtasia project](https://support.techsmith.com/hc/en-us/articles/13010049964941-How-to-Share-a-Camtasia-Project-with-Another-User)
- [Legacy CAMPROJ and CAMREC migration](https://support.techsmith.com/hc/en-us/articles/360048452272-Opening-Camproj-and-Camrec-Files-in-Camtasia-2020-and-Later)
- [Cloud storage compatibility](https://support.techsmith.com/hc/en-us/articles/203732738-Cloud-Storage-Compatibility-FAQ)

## Licensing and deployment

- [Deploying TechSmith products](https://support.techsmith.com/hc/en-us/articles/43771074923021-Deploying-TechSmith-Products)
- [Activate Snagit or Camtasia](https://support.techsmith.com/hc/en-us/articles/45353457739149-How-to-Activate-Snagit-or-Camtasia)
- [Subscription activation models](https://support.techsmith.com/hc/en-us/articles/31352249532941-How-Do-I-Activate-My-Snagit-or-Camtasia-Subscription)
- [Offline Camtasia activation](https://support.techsmith.com/hc/en-us/articles/42881382263309-Activate-Camtasia-Editor-Offline)
- [Current download and update guidance](https://support.techsmith.com/hc/en-us/articles/45436108931341-Download-Install-or-Update-Snagit-Camtasia)

## Pinned interpretation

- Snagit COM is Windows-only and current, but it must be checked against the installed type library. The official ProgID is `Snagit.ImageCapture.1`; official PowerShell samples also use `SNAGIT.ImageCapture`.
- Current image-input enum values are desktop `0`, window `1`, and region `4`; image outputs are file `2` and clipboard `4`. Do not reuse the incorrect historical values previously published by this pack.
- `Capture()` is asynchronous. Wait for `IsCaptureDone`, then inspect `LastCaptureSucceeded` and `LastFileWritten` when file output is selected.
- Camtasia 2022 and later use `CamtasiaRecorder.exe` for documented recorder commands. Old short switches and legacy recorder executable names are historical only.
- The legacy Camtasia exporter was removed in 2024.1.3. Do not prescribe `CamtasiaProducer.exe` for a current installation.
- Active Camtasia projects and media belong on a local, non-synced drive. Archive or synchronize only after Camtasia has closed.
- Individual subscriptions activate by sign-in. Business licenses use keys and support managed or offline activation. Treat keys and activation artifacts as secrets.
