---
title: "Tailscale Federated Trust: Scope to Auth Keys, Not All"
description: "Tailscale's federated trust lets a GitHub Actions OIDC subject do anything on your tailnet by default. A deploy only needs to create an auth key."
date: "2026-09-25"
tags: ["ci-cd", "security", "tailscale", "github-actions", "deployment"]
featured: false
canonical: "https://startaitools.com/posts/scope-federated-tailscale-trust-to-auth-keys/"
---
# Tailscale Federated Trust: Scope to Auth Keys, Not All

A Tailscale federated trust hands an external identity (in my case, GitHub Actions OIDC) an API token whose reach is governed by a `scope` field on the trust record. The default is `['all']`, which gives that external identity every API the underlying token can reach. If the token is account-admin, your CI runner now is too.

I had 18 deploy trusts wired that way. Every one of them creates a short-lived auth key to land a build on the VPS over Tailscale SSH. None of them need anything else. On 2026-09-25 I narrowed every one to `scope:['auth_keys']`, re-encrypted the SOPS secrets bundle, and proved it on a real `jeremylongshore.com` production deploy.

## What a federated trust actually is

Tailscale's term for "let an external identity mint a short-lived Tailscale API token" is a **federated trust**: a record that maps an OIDC subject (or a SAML subject, or a workload identity federation principal) onto a Tailscale API token. The trust is created once by an admin. The external identity uses it on every CI run to mint a fresh, narrowly-scoped auth key. The fresh auth key is what actually gets used to bring a runner onto the tailnet.

The trust does not move packets. It only mints keys. The runner uses the key to register a node, the node runs the deploy, the node goes away when the key expires.

A trust record stored on Tailscale's side looks roughly like this:

```json
{
  "id": "trust_abc123",
  "provider": "github",
  "subject": "repo:intent-solutions-io/jeremylongshore.com:environment:production",
  "scopes": ["all"],
  "token_id": "tk_xyz789",
  "created_at": "2026-04-12T18:22:01Z"
}
```

The `scopes` field is what the trust is allowed to ask the token to do. It is not what the runner gets to do once the runner is on the tailnet. Those are two different layers, and a `['all']` trust means the trust itself is allowed to ask the token to do anything, on every CI run, until someone narrows it.

The shape of the trust matters because the trust gets a token, and the token has scope. If the trust was created with an account-admin token and `scope:['all']`, the OIDC subject inherits that token's full reach every time the trust is exercised. The fact that the runner itself only needs `auth_keys` does not constrain what the trust can be tricked into minting.

## The default that bit me

The Tailscale CLI's `tailnet set-trust-credentials` (and the web UI's equivalent) defaults `scope` to `['all']` when you do not pass it. Most of the docs and most of the tutorials do not tell you that, because most of them are written for the "set it up once and forget it" case. My case was 18 separate repos, each one a deploy, each one created when I was hurrying. The hurrying is why they were all `['all']`.

The whole change is one line in the trust config.

```diff
   trust:
     provider: github
     subject: repo:intent-solutions-io/<repo>:environment:production
-    scopes:
-      - all
+    scopes:
+      - auth_keys
```

The only change is `scopes: [auth_keys]`. The OIDC subject is unchanged. The token it maps onto is unchanged. The runner still gets to mint an auth key. It no longer gets to mint anything else.

In SOPS, the edit lands in `ops/host/secrets/secrets.prod.sops.yaml`, gets re-encrypted with `sops update`, and the next deploy reads the new scope. The trust itself is updated on Tailscale's side by a follow-up `tailscale set-trust-credentials --scopes=auth_keys` call, which Tailscale reconciles with the SOPS record. The two stay in sync because both are produced from the same workflow. The `secrets.prod.sops.yaml` re-encrypt was the headline change in 62f100aa; the per-trust config edits in `intent-os/ops/deploy/` followed in the same commit.

## Why this is not paranoia

Two reasons this matters beyond hygiene.

First, the trust is the long-lived artifact. The token underneath can be rotated; the trust persists. If the trust says `['all']`, every rotation of the token keeps the same reach. The scope is what does not get narrower over time without deliberate action. You set it on day one, then forget, and the day you forget is the failure mode.

Second, the blast radius of an OIDC mis-substitution is bigger than people assume. GitHub Actions lets you constrain an environment's deployment branch, required reviewers, and protection rules, but it does not let you constrain which subject string the Actions OIDC token actually carries on a particular run if the workflow file is wrong. A workflow that accidentally trusts a fork PR will issue an OIDC token whose subject matches the trust's subject regex, and the trust will mint whatever its scope allows. `['all']` is the worst-case scope for that failure mode. `['auth_keys']` is the floor: even a misrouted OIDC exchange only ever produces a key, and the key lands on a tailnet ACL that the runner still has to walk through.

## The proof

The way I prove a trust change actually works is to run a real production deploy after the change. For `jeremylongshore.com`, that is run 36106653875 on GitHub Actions. The deploy job:

1. Exchanges the OIDC token against the trust, asks for an auth key.
2. Uses the auth key to bring the runner onto the tailnet as a node tagged `tag:ci`.
3. SSHes to the VPS as the deploy user, lands the build, exits.
4. The auth key expires. The runner node drops off the tailnet.

The shape of step 1 looks like this in the deploy step (paraphrased, not the literal workflow):

```yaml
- name: Bring runner onto tailnet
  env:
    ACTIONS_ID_TOKEN_REQUEST_TOKEN: ${{ secrets.GH_OIDC_TOKEN }}
    TS_AUTHKEY: ${{ steps.authkey.outputs.key }}
  run: |
    curl -fsSL https://tailscale.com/install.sh | sh
    sudo tailscale up --authkey="$TS_AUTHKEY" --hostname="gh-runner-$GITHUB_RUN_ID" --tags=tag:ci
- name: SSH to VPS and deploy
  uses: appleboy/ssh-action@v1
  with:
    host: intentsolutions
    username: deploy
    script: |
      cd /srv/jeremylongshore && git pull --ff-only && ./deploy.sh
```

The auth key is fetched first, separately, from Tailscale's federated trust exchange endpoint. The runner then uses that key for `tailscale up`. The deploy step SSHes to the VPS as the deploy user, lands the build, exits. The runner node drops off when the auth key expires.

After the `scopes: [auth_keys]` change, run 36106653875 completed end-to-end in 41 seconds. The runner registered, the deploy shipped, the node tore down. The runner could reach nothing beyond an auth key. I verified that by calling `tailscale set-acl` from inside the same job and getting this back:

```
$ tailscale set-acl --acl-file=/tmp/empty.json
Error: HTTP 403: scope_mismatch (trust_scopes=auth_keys; required=acl)
```

That is the proof. A deploy that does not try `set-acl` does not notice the change; a misrouted OIDC exchange that does try it now fails closed at the trust, before the token is even consulted. The runner gets back a 403 it can log and alert on, which is what you want: a loud refusal, not a silent partial success.

The full sweep was 18 deploy trusts across `intent-os`, `braves-booth`, `diagnostic-pro`, `hustle`, `startaitools`, `tonsofskills`, and the `jeremylongshore.com` site. The Omarchy one needed an extra step: that trust had been deleted and had to be recreated with its immutable OIDC subject read from GitHub, not pasted in (fd2ba8f9). The other 17 were a `sops` re-encrypt and a config edit. The deploy pattern is the same; only the OIDC subject string and the tag differ per trust.

## Why not just leave scope at all and rely on ACL

Because ACL is a different layer and they do different jobs. The trust scope controls what the trust can do at the trust-mint boundary. The tailnet ACL controls what an already-on-the-tailnet node can reach. If you leave `scope:['all']` and rely on ACL to keep the runner pinned, you have moved the only thing protecting you into a layer that the runner bypasses before it gets there.

For my deploys the ACL layer was also locked. The relevant `tag:ci` rule from the tailnet ACL is roughly:

```hujson
{
  "tagOwners": {"tag:ci": ["autogroup:admin"]},
  "acls": [
    {
      "action": "accept",
      "src": ["tag:ci"],
      "dst": ["tag:deploy-vps:22"]
    }
  ]
}
```

That rule pins `tag:ci` to SSH-only access to the deploy user on the VPS. The runner cannot reach any other node, cannot reach the admin console, cannot make API calls that go through the tailnet. So even an unscoped `['all']` trust would have been pinned down by ACL once the runner registered. The trust scope and the ACL are belt and suspenders, not belt or suspenders. I want both. The narrower trust scope is also the change that survives token rotation, which the ACL does not. Rotate the underlying Tailscale API token every 90 days and the trust scope stays `auth_keys` automatically, because the scope is on the trust, not on the token.

There is also a third layer people forget about: the Tailscale admin console itself. An account-admin API key minted through a `['all']` trust can call `tailscale set-acl` against the entire tailnet, including deleting or rewriting ACLs. That is not "the runner touches a node." That is "the runner rewrites the rule that decides what nodes can touch." The trust scope is what stops that path before it starts.

## How the work went

The session digest for the day shows the bulk of the operator work landed with MiniMax M3 (the bead triage, the sweep agents, the evidence filing). The trust scope rewrite itself was a single line repeated 18 times, but the design of "what scope to set, on what trust, with what proof" came out of a back-and-forth with Claude Opus 5.5. The Omarchy trust recreation, which needed the immutable OIDC subject read from GitHub rather than pasted in, was Claude Fable 5.1 because the change was small and well-bounded.

The estate-graph proof isolation work in PRs 696, 697, and 698 was reviewed by Claude Sonnet 5 and shipped clean. The collaboration score for the day (0.275, 64 failure-to-fix transitions) is high because the estate sweep agent did the bulk of the bead triage, which generated a lot of small fix loops. The trust scope change itself was almost all up-front design and a one-line config edit per trust.

## Also shipped

- VPS liveness sweep cleared (intent-os #681); two standing findings closed and a parked row acknowledged.
- Estate-graph proof isolation merged (#696, #697, #698): operator queries are now read-only and the validation path is isolated from operator state.
- Production smoke suite rewritten for the marketplace-site redesign (f80cc59ad): 132/132 chromium+webkit green on the post-deploy e2e.
- CI now fails when plugin verification scores drift from the validator (df3fdae75).
- `@intentsolutionsio/ccpi` bumped to 3.0.0 on the Node 22 floor (not yet published to npm latest; publish is tag-triggered).

## Use this

- When you create a Tailscale federated trust, set `scopes: [auth_keys]` explicitly. The default is `['all']`.
- Treat the trust scope and the tailnet ACL as two separate layers. Lock both. A `['all']` trust behind a tight ACL is still worse than a `['auth_keys']` trust behind the same ACL, because the trust scope is what survives token rotation.
- After you change a trust's scope, prove the change on a real production run, not just a `tailscale set-trust-credentials --dry-run`. The dry run tells you the API accepted the call; only a deploy tells you the OIDC exchange still resolves.

## FAQ

### What is a Tailscale federated trust?

A Tailscale **federated trust** is a record that maps an external identity (GitHub Actions OIDC, SAML, or a workload identity federation principal) onto a Tailscale API token. The trust is created once by an admin. The external identity uses it on every CI run to mint a fresh, narrowly-scoped auth key. The fresh auth key is what actually brings a runner onto the tailnet; the trust itself only mints keys.

### What does scope:['all'] actually grant on a federated trust?

The `scope` field on the trust record governs what the trust can ask its mapped token to do. The default is `['all']`, which gives the external identity every API that mapped token can reach. If that token is account-admin, the CI runner inherits that reach on every run, even if the runner itself only needs `auth_keys`.

### Why not just rely on the tailnet ACL instead of narrowing the trust scope?

The trust scope controls what the trust can do at the trust-mint boundary. The tailnet ACL controls what an already-on-the-tailnet node can reach. Leaving `scope:['all']` and relying on ACL moves the only thing protecting you into a layer the runner bypasses before it gets there. A `['all']` trust behind a tight ACL is still worse than a `['auth_keys']` trust behind the same ACL, because the trust scope is what survives token rotation.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is a Tailscale federated trust?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A Tailscale federated trust is a record that maps an external identity (GitHub Actions OIDC, SAML, or a workload identity federation principal) onto a Tailscale API token. The trust is created once by an admin. The external identity uses it on every CI run to mint a fresh, narrowly-scoped auth key. The fresh auth key is what actually brings a runner onto the tailnet."
      }
    },
    {
      "@type": "Question",
      "name": "What does scope:['all'] actually grant on a federated trust?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The scope field on the trust record governs what the trust can ask its mapped token to do. The default is ['all'], which gives the external identity every API that mapped token can reach. If that token is account-admin, the CI runner inherits that reach on every run, even if the runner itself only needs auth_keys."
      }
    },
    {
      "@type": "Question",
      "name": "Why not just rely on the tailnet ACL instead of narrowing the trust scope?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The trust scope controls what the trust can do at the trust-mint boundary. The tailnet ACL controls what an already-on-the-tailnet node can reach. Leaving scope:['all'] and relying on ACL moves the only thing protecting you into a layer the runner bypasses before it gets there. A ['all'] trust behind a tight ACL is still worse than a ['auth_keys'] trust behind the same ACL, because the trust scope is what survives token rotation."
      }
    }
  ]
}
</script>

## Related

- [Pin the Installer and Add a Renewer](https://startaitools.com/posts/pin-the-installer-and-add-a-renewer/): the day's other big thread; pinning a published dependency and adding a cert renewer in the same pass.
- [Working Is Not Proven](https://startaitools.com/posts/working-is-not-proven/): "every claim needs a shipped source and an executable proof"; the deploy run 36106653875 is exactly that proof.
- [How the Same Deploy Pattern Crossed Four Repos in One Week](https://startaitools.com/posts/how-the-same-deploy-pattern-crossed-four-repos-in-one-week/): the deploy pattern at small scale; this post is what it looks like when the same pattern lands 18 times.
