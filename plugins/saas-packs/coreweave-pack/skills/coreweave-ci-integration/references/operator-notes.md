# CI trust and recovery boundaries

Configure the protected `coreweave-staging` environment, required reviewers, secret and environment variables before using the example. The environment name alone does not prove approval protection exists. Use a dedicated namespace-scoped staging identity and a reviewed manifest with a tested image digest; a secret reference in a pull-request workflow must not expose deploy credentials.

Use GitHub-hosted isolated PR runners. Do not run fork/PR code on the shared Buzz deployment runner, use pull_request_target to check out PR code, or share a privileged deployment cache with untrusted jobs. Dependencies run code during installation; that is acceptable only in the isolated, credential-free unit lane.

Server dry-run is an admission check, not a runtime or capacity test. After an approved staging apply, verify model readiness and a non-sensitive acceptance check. A Deployment rollout alone does not verify application quality. A rollback must select the retained prior revision and recover separately changed data/configuration under their own procedures.

Source: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
