<!-- doc-class: record -->

# tonsofskills.com Security-Warning Reports: Incident Record

- **Date:** 2026-09-27 (investigation 19:08 to about 21:30 UTC, two phases)
- **Severity:** P2. The site is up and serving worldwide, but visitors behind security products that trust specific threat-intelligence feeds are blocked or warned.
- **Status:** Origin and VPS cleared. One infrastructure defect fixed. External reclassification appeals prepared and awaiting owner approval; nothing has been submitted to any vendor.
- **Filing note:** the brief suggested `000-docs/incidents/`. This repo files after-action records flat in `000-docs/` as `NNN-AA-AACR-*` (see 812), so this record follows the repo convention.
- **Domain notation:** the retired alias `claudecodeplugins[.]io` is written defanged. The repository's dead-domain policy (`scripts/dead-domain-policy.mjs`) treats a literal mention in first-party files as actionable.

## Answers

| Question | Answer |
|---|---|
| A. Is tonsofskills.com compromised? | **No evidence of compromise.** The deployed files match the git release, there is no injected JavaScript, no malicious redirects, and no web shells (see the Compromise status table). |
| B. Is the VPS compromised? | **NO EVIDENCE OF VPS COMPROMISE FOUND** (see the Compromise status table for the exact checks). |
| C. Who is blocking it? | **Proven:** 12 VirusTotal URL engines flag the apex as malicious and 1 as suspicious. Cisco Talos rates it "Untrusted". DNS4EU/Whalebone and CIRA Canadian Shield block it at DNS. **Inferred:** consumer and mobile security apps and enterprise gateways built on those feeds. |
| D. What caused each classification? | Vendors have not disclosed the trigger content. The labels they return are phishing (4 engines), malware (3), generic malicious (5), plus 1 suspicious (ESET), "Exploits / Malicious Sites" (Talos), and "Malware Blocked" (CIRA). **Proven:** this is a domain-level verdict (the IP is clean on 91/91 VirusTotal engines), and the current ZIP builds have never been submitted to VirusTotal. The most likely triggers are inferred below. |
| E. What must change vs what can be appealed? | Every proven classifier can be **appealed** as a false positive. No site change is proven to be required. Reputation-hardening proposals (class B) and speculative ones (class C) are listed below; none were implemented. |

## Reputation matrix (as of 2026-09-27)

Legend: **P** = proven by a lookup in this investigation; **I** = inferred.

| Provider / scanner | Current classification | Exact URL flagged | Scope | Detection or category | First seen | Evidence | False-positive appeal | Appeal status | Recommended remediation |
|---|---|---|---|---|---|---|---|---|---|
| **VirusTotal (aggregate)** | 12 malicious, 1 suspicious, 32 undetected, 46 harmless (apex); 9 malicious, 1 suspicious (`www`) | `http://tonsofskills.com/` (12 malicious, last analysis 2026-09-27 14:28Z); `https://tonsofskills.com/` (11 malicious, last analysis 2026-09-10); `https://www.tonsofskills.com/` (9 malicious) | Domain + URL | see engine rows below | URL first submitted 2026-03-06; when detections began is not exposed | P: `www.virustotal.com/ui/domains/…` and `/ui/urls/<sha256>` | Per engine (VirusTotal cannot overrule an engine) | Not submitted | Appeal to each flagging engine, then request a rescan |
| VirusTotal: IP `167.86.106.29` | Clean, 0 of 91 | n/a | IP | none | n/a | P: `/ui/ip_addresses/167.86.106.29` | n/a | n/a | None |
| VirusTotal: 18 bundle ZIPs + all-in-one ZIP (current build hashes) | Unknown to VirusTotal | `/downloads/bundles/*.zip`, `/downloads/claude-code-plugins-all.zip` | Downloadable file | none; the hashes have never been submitted | n/a | P: `/ui/files/<sha256>` returns NotFound for all 19 | n/a | n/a | Current file hashes cannot be the trigger. URL-level bundle verdicts are blocked by the UI reCAPTCHA (see gaps) |
| ADMINUSLabs | malicious | apex (`http` and `https`) | URL/domain | `malicious` | unknown | P (VT) | vendor contact via VT engine page | Not submitted | Appeal |
| alphaMountain.ai | malicious | apex, `www` | URL/domain | `phishing`; category "Phishing" | unknown | P (VT) | alphaMountain URL dispute form | Not submitted | Appeal |
| **Bitdefender** | malicious | apex, `www` | URL/domain | `phishing` | unknown | P (VT) | Bitdefender false-positive submission (URL) | Not submitted | **Appeal first.** Bitdefender's engine and data are widely licensed in consumer and mobile products (I) |
| Chong Lua Dao | malicious | apex, `www` | URL/domain | `malicious` | unknown | P (VT) | chongluadao.vn report form | Not submitted | Appeal |
| ESET | suspicious | apex, `www` | URL/domain | `suspicious` | unknown | P (VT) | ESET false-positive submission | Not submitted | Appeal |
| Forcepoint ThreatSeeker | malicious | apex | URL/domain | `malicious`; category "malicious web sites" | unknown | P (VT) | csi.forcepoint.com | Not submitted | Appeal |
| **Fortinet** | malicious | apex, `www` | URL/domain | `malware` | unknown | P (VT); FortiGuard lookup page returned 403 to a script | FortiGuard web-filter rating submission | Not submitted | Appeal (FortiGate and FortiClient enforce this, I) |
| G-Data | malicious | apex, `www` | URL/domain | `phishing` | unknown | P (VT) | G DATA false-positive submission | Not submitted | Appeal |
| Lionic | malicious | apex, `www` | URL/domain | `malicious` | unknown | P (VT) | Lionic contact | Not submitted | Appeal |
| SafeToOpen | malicious | apex | URL/domain | `phishing` | unknown | P (VT) | SafeToOpen contact | Not submitted | Appeal |
| **Sophos** | malicious | apex, `www` | URL/domain | `malware`; category "spyware and malware" | unknown | P (VT) | Sophos submission portal | Not submitted | Appeal |
| VIPRE | malicious | apex, `www` | URL/domain | `malware` | unknown | P (VT) | VIPRE false-positive submission | Not submitted | Appeal |
| **Webroot (OpenText / BrightCloud)** | malicious | apex, `www` | URL/domain | `malicious`; category "Phishing and Other Frauds" | unknown | P (VT) | BrightCloud URL/IP lookup and change request | Not submitted | Appeal (BrightCloud data is licensed into many firewalls and routers, I) |
| **Cisco Talos** | Web reputation **Untrusted**; content category Computers and Internet; threat categories Exploits, High Risk Sites and Locations, Malicious Sites | `tonsofskills.com`, `www.tonsofskills.com` | Domain | reputation rules `sunbelt_bp_misc_exploits_url`, `trd_mali`, `trdw_ship4rank` | unknown | P: `talosintelligence.com/cloud_intel/url_reputation` | talosintelligence.com reputation dispute (needs a Cisco/Talos account) | Not submitted | Appeal. Talos drives Cisco Umbrella, Meraki and Secure Web Appliance blocks (I). The alias `claudecodeplugins[.]io` is rated "Questionable" (`trdw_ship4rank` only). |
| **DNS4EU (Whalebone threat feed)** | Blocked: "potentially malicious website" | `tonsofskills.com`, `www.tonsofskills.com` at DNS | Domain | category not disclosed; no EDE reason; sinkhole ID `6000063` | unknown | P: `dig @86.54.11.1` returns `51.15.69.11`; block-page text | https://joindns4.eu/for-public | Not submitted | Appeal |
| **CIRA Canadian Shield** | Blocked (Protected and Family tiers) | `tonsofskills.com`, `www.tonsofskills.com` at DNS | Domain | EDE 17 "Filtered: CIRA Canadian Shield - Malware Blocked" | unknown | P: `dig @149.112.121.20` | https://www.cira.ca/en/why-am-i-seeing-block-page/ | Not submitted | Appeal |
| Google Safe Browsing | Clean (status 1) | none | Domain | none | n/a | P: transparency-report API | n/a | n/a | None. Native Chrome and Safari red warnings are therefore **not** the cause. |
| Microsoft SmartScreen / Defender | **Unknown** (not queryable without a Windows client) | n/a | n/a | n/a | n/a | not checked | Microsoft WDSI "incorrectly detected" URL submission (Microsoft account) | Not submitted | Check from a Windows/Edge client before appealing |
| Spamhaus DBL / ZEN | Not listed | none | Domain / IP | none | n/a | P: authoritative query with test point answered | n/a | n/a | None |
| URLhaus (abuse.ch) | Not listed in the public host list | none | Domain | none | n/a | P: 0 hits in `urlhaus.abuse.ch/downloads/hostfile/`; the API needs an Auth-Key | n/a | n/a | None |
| SURBL / URIBL | Not listed | none | Domain | none | n/a | P: test points answered | n/a | n/a | None |
| Cloudflare (1.1.1.2 malware, 1.1.1.3 family resolvers) | Not blocked | none | Domain | none | n/a | P: both return `167.86.106.29` | Radar domain-feedback form | n/a | None. Radar categorization itself was not queried (needs an API token). The site does not use Cloudflare as a CDN. |
| Quad9, OpenDNS/FamilyShield, AdGuard, CleanBrowsing, ControlD, Comodo, Yandex, UltraDNS, SafeDNS, OpenBLD, NextDNS anycast | Not blocked | none | Domain | none | n/a | P: resolver matrix | n/a | n/a | None |
| AlienVault OTX, OpenPhish, urlscan.io | Clean | none | Domain / IP | none | n/a | P | n/a | n/a | None |

## Root cause per symptom

| Report | Finding | Proven vs inferred |
|---|---|---|
| Teammate on iPhone: Chrome `ERR_SSL_PROTOCOL_ERROR` ("sent an invalid response") plus "my security apps are flagging ToS" | An on-device mobile security app or web filter using one of the flagging feeds blocks the connection. It cannot show a valid certificate for the blocked host, so it resets the connection or injects non-TLS bytes, and Chrome reports a protocol error. The app raises its own notification. | **The feeds are proven; the app is inferred.** Candidates, based on the engines that actually flag the site: Bitdefender and products built on it, Sophos Intercept X for Mobile, ESET, Webroot/BrightCloud-based products, Fortinet FortiClient, and Cisco Umbrella/Secure Client (Talos). Avast and McAfee do **not** flag the site on VirusTotal, which lowers Gen Digital and McAfee as candidates. |
| "TOS violation" alert (reported as an Oregon user) | **Leading hypothesis: this is the same teammate's text, misread.** His message said "My security apps are flagging ToS", and in context "ToS" almost certainly means **Tons of Skills**, not Terms of Service. | **Inferred, but the strongest reading.** No provider (Porkbun, Contabo, Let's Encrypt, Google, Microsoft, Cloudflare) sent any ToS, abuse or suspension notice (mailbox searched since 2026-08-01). No page on the site says "violation". Of the two vendor block pages that literally use Terms of Service/Use wording: Cloudflare's covers only sites proxied through Cloudflare (this one is not), and Microsoft's "violates the Acceptable Use Policy located in the Terms of Use" covers content hosted on Microsoft services. **Confirm with the teammate.** |
| Overseas user: certificate errors | A protective DNS resolver (DNS4EU, or an ISP resolver on the same Whalebone feed) answers with a sinkhole that presents a certificate for `doh.joindns4.eu`. The browser reports a name mismatch, and HSTS removes the click-through. | **Mechanism proven end to end.** That this particular user was on such a resolver is inferred. |
| Others: large warning pages | Vendor block pages or sinkhole certificate interstitials. They are not Google Safe Browsing, which is clean. | Inferred from the matrix. |

### Most likely triggers (inferred; no vendor has disclosed its reason)

1. **Brand-lookalike alias domains.** Three domains containing the "Claude" mark 301 to a young domain (registered 2026-03-04), and Talos already rates the alias "Questionable". Lookalike-domain-to-redirect is a classic phishing signal. Four engines say "phishing".
2. **Brand-named pages.** Hundreds of vendor-named "packs" (Salesforce, Adobe, Shopify, Stripe and others), each with a download button, on a young domain. This fits brand-impersonation phishing heuristics.
3. **Offensive-security vocabulary.** "exploit" appears 86 times across the HTML, plus a penetration-tester plugin. Talos's rule `sunbelt_bp_misc_exploits_url` and its "Exploits" threat category match this directly.
4. **Downloadable archives and pipe-to-shell commands** on the same origin: more than 400 ZIPs, including the security and crypto bundles, and 11 pages with `curl ... | sh`. The current ZIP hashes are unknown to VirusTotal, so a file-hash detection of the current build is ruled out; earlier builds remain unknown.

## Why the outcome differs by region

There is **no CDN** and **no AAAA record**. Every visitor worldwide reaches the same IPv4 origin, so differences come only from the visitor's resolver, endpoint software or network gateway:

- **European Union:** DNS4EU is the EU-backed public resolver, and Whalebone's feed also powers ISP resolvers in several European countries. Users on those resolvers get the sinkhole, which shows as a certificate error.
- **Canada:** CIRA Canadian Shield (free, and promoted to Canadian households) returns "Malware Blocked", which shows as an HTTPS timeout.
- **Everywhere:** endpoint and mobile security apps (Bitdefender, Sophos, ESET, Webroot-based and Fortinet products) and enterprise, school or ISP gateways (Talos/Umbrella, FortiGuard, Forcepoint) block regardless of region.
- **Unaffected:** default ISP resolvers without threat filtering, Google/Cloudflare/Quad9 public DNS, and the 40 check-host.net nodes in 25 countries (all returned HTTP 200).

## IPv4 and IPv6

| Check | IPv4 | IPv6 |
|---|---|---|
| A / AAAA for the apex and `www` | A `167.86.106.29` on all four Porkbun authoritative servers and every resolver tested | **No AAAA** on the four authoritative servers, six public resolvers, or 20 check-host nodes. No stale AAAA exists anywhere. |
| Certificate presented | `CN=tonsofskills.com` (YE2) and `CN=www.tonsofskills.com` (YE1), verify 0 | Not reachable by name. Forced to the host's IPv6 address with `curl --resolve`, the same valid certificate is served (verify 0). |
| HTTP response | `http://` returns 308, then `https://` returns 200 (1 hop) for both names | Forced: 308, then 200 |
| Final origin | `https://tonsofskills.com/` and `https://www.tonsofskills.com/` (`www` does not canonicalize to the apex) | n/a |

Conclusion: IPv6 plays no part. No name points to it, and the host would serve correctly if one did.

## TLS findings (summary)

- SSL Labs grade A+, `chainIssues=0`, trusted in the Mozilla, Apple, Android, Java and Windows stores. The chain validates against X1-only and X2-only stores; a negative control with an unrelated root fails. TLS 1.2 and 1.3 only.
- Connections without SNI, or with an unknown name, get alert 80 (Caddy's default). This is a mechanism, not a cause, because every browser sends SNI.
- **Latent defect:** h3 is advertised, but UDP 443 is not allowed by the firewall, so QUIC times out and browsers fall back to TCP silently. Estate-wide; not changed.
- Certificate Transparency shows no unexpected issuance. The wildcard certificates are Porkbun's automatic registrar SSL.

## Compromise status

### Site (tonsofskills.com)

| Item | Result | Exact check performed |
|---|---|---|
| Injected JS | NOT FOUND | All 3,710 HTML pages parsed. External `<script src>` origins are only `analytics.intentsolutions.io` and `www.googletagmanager.com`. All 25 distinct inline scripts, hashed across pages, are identifiable site UI code. No `<iframe>`, no service worker. |
| Modified production files | NOT FOUND | Live `dist` is the symlinked release `fd4873c0b` (= `origin/main`). All 4,187 files carry the deploy timestamp and none is newer. The file set equals the previous release plus the one blog directory that commit added. The live security-headers snippet is byte-identical to the repo. |
| Malicious redirects | NOT FOUND | Every redirect hop traced for the apex, `www`, and all six alias names. Only 308 (HTTP to HTTPS) and 301 to the canonical host. |
| Web shells | NOT FOUND | No `.php`, `.phtml`, `.jsp`, `.asp`, `.cgi` or `.pl` files under the `/srv` web roots or in the live release; no PHP runtime installed; Caddy serves static files only. |

### VPS

| Item | Result | Exact check performed |
|---|---|---|
| Unauthorized SSH access | NOT FOUND | SSH journal since 2026-08-27: 24,495 accepted logins, all public-key, all from the private admin network; 0 failed or invalid-user attempts. The firewall allows SSH only from that network. `last`/`wtmp` shows no unknown account. |
| Malicious processes / cryptominers | NOT FOUND | Top-CPU process list (monitoring and Docker only, load average 1.5 to 2.7). Name/argument scan for xmrig, minerd, kinsing, kdevtmpfsi, stratum, reverse shells, and binaries running from `/dev/shm` or `/tmp`: no matches. The "(deleted)" executables are long-running daemons that predate package upgrades. |
| Unexpected containers | NOT FOUND | `docker ps -a`: every container belongs to a documented stack (Plane, ERPNext, Twenty, Umami, Scorecard Echo, DiagnosticPro, Hustle, Buzz, Documenso, NOW-LMS, radicale, SigNoz staging keeper, jeremylongshore-web, the GitHub-webhook database, and Watchtower). |
| Unexpected outbound connections | NOT FOUND | `ss -tunp state established`, client-side connections only: Tailscale control and DERP relays (whois Tailscale Inc.; `derp26c`, `derp12e`, `derp18c`, `lb.fra` hostnames) and `docker-proxy` to internal container addresses. |
| Unauthorized cron / systemd jobs | NOT FOUND | No user crontabs. `/etc/crontab`, `cron.d`, `cron.daily` and `cron.hourly` contain only OS, monitoring and backup entries. Every timer and every unit changed in the last 30 days maps to a known estate service or a package update. |
| Tampered system binaries | NOT FOUND | `dpkg -V` on openssh-server, coreutils, procps, iproute2, sudo, login, passwd, curl and caddy is clean apart from config files. The `sudo` and `curl` binary changes match apt security upgrades on 2026-09-23 and 2026-09-25. |

**NO EVIDENCE OF VPS COMPROMISE FOUND.** Supporting evidence: the ten checks above, all read-only.

## Changes made

1. Added the missing DNS record `A www.claudecoworkskills.io -> 167.86.106.29` (TTL 600) at Porkbun, via `intent-os/ops/dns/porkbun-update-record.sh`. This was an existing P2 finding (`dns-registrar-tls-3`): Caddy had been failing ACME validation for that name on every reload, 50 errors since 09-20. Rollback: `porkbun-update-record.sh claudecoworkskills.io delete A www ''`.
2. Ran `caddy validate`, then a graceful `systemctl reload caddy` (no restart, config unchanged). The certificate was issued at 19:30:15Z, and the name now 301s to the canonical host.
3. Nothing else changed: no content, header, TLS, firewall or cache changes, and no vendor submissions.

## Proposed changes, classified (none implemented)

| Class | Proposal | Tied evidence |
|---|---|---|
| A (confirmed root-cause remediation) | False-positive appeals to every proven classifier: the 13 VirusTotal engines, Talos, DNS4EU/Whalebone, CIRA | Each has a proven verdict in the matrix |
| A | (Done) fix the `www.claudecoworkskills.io` DNS/ACME defect | Caddy journal + NXDOMAIN, now resolved |
| B (reputation hardening) | Publish `/.well-known/security.txt` with an abuse contact | Currently 404; reviewers check for it |
| B | Decide the future of the three trademark-lookalike alias domains (keep as redirects, or retire them) | Talos rates the alias "Questionable"; lookalike-domain redirect is a phishing heuristic (inferred link) |
| B | 301 `www.tonsofskills.com` to the apex | Two hosts are scored separately (9 and 12 engines) |
| B | Serve bundle ZIPs from GitHub Releases or a separate download domain | Keeps file-level detections off the catalog domain (no current file detection) |
| B | Fix HTTP/3: allow 443/udp or stop advertising h3 (estate-wide) | aioquic handshake timeout |
| C (speculative) | Replace inline `curl ... | sh` with links to vendor install pages | No vendor has cited it |
| C | Reword offensive-security and crypto plugin pages | Talos "Exploits" is suggestive, not proof |
| C | `default_sni` for SNI-less clients | No report implicates an SNI-stripping proxy |

## Appeal text (prepared, not submitted)

Use for each vendor, adjusting the classification line:

> **URL:** https://tonsofskills.com/ (also https://www.tonsofskills.com/)
> **Current classification:** [vendor's label, for example "Phishing" / "Malware" / "Untrusted: Exploits, Malicious Sites"]
> **Why this is a false positive:** tonsofskills.com is the public catalog for Tons of Skills, an open-source marketplace of plugins and skills for Claude Code and other AI coding agents. Source is public at https://github.com/jeremylongshore/tons-of-skills-marketplace (MIT license, about 2,800 stars and 400 forks, public since October 2025). The site is a static site generated from that repository. It collects no credentials or payment data, runs no third-party advertising, and imitates no brand's login or checkout. Vendor names on plugin pages describe integrations. Downloads are source-only plugin bundles (Markdown, Python, JSON, YAML, shell templates; no executables). Security-category plugins are defensive tooling documentation.
> **Security controls:** HTTPS only with HSTS (1 year, includeSubDomains), a strict Content-Security-Policy, `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, a restrictive Permissions-Policy, and Let's Encrypt certificates.
> **Independent checks:** Google Safe Browsing clean; Spamhaus DBL, SURBL, URIBL and URLhaus not listed; VirusTotal shows the hosting IP clean on 91/91 engines.
> **Operator:** intentsolutions.io LLC, 26050 Equity Drive, Ste E - 1062, Daphne, AL 36526. Contact: jeremy@intentsolutions.io.
> Please re-review and reclassify as Information Technology / Software Development.

Do not claim Anthropic partner status in appeals unless it is separately verified.

## Monitoring (specified, not built)

The dev box's `intent-os/ops/observability/outside-in-collector.sh` runs every 2 minutes and is healthy, but it does not probe tonsofskills today. The extension, specified here for an intent-os change:

1. HTTP probes for the apex and `www`, and 301 probes for each alias.
2. A certificate-chain check against an X1-only trust store, plus days-to-expiry.
3. A DNS drift check on A, AAAA and NS.
4. An hourly reputation check:
   - DNS4EU and CIRA answers (each paired with a control domain).
   - Spamhaus DBL and SURBL, each gated on its test point.
   - Google Safe Browsing status.
   - Talos threat level.
   - VirusTotal malicious count, via an API key once one exists.

It alerts through the existing `af_dispatch` Slack floor. Ship it with the current failed state as the baseline, so that recovery is observed.

## Gaps

- **VirusTotal URL verdicts for individual download and install-script URLs, and for the alias domains:** the unauthenticated UI endpoints began returning `RecaptchaRequiredError` after the domain, IP and top-level URL lookups. A free VirusTotal account API key removes this; it takes an owner signup.
- Microsoft SmartScreen and Cloudflare Radar categories were not queried.
- The dates on which individual vendors first flagged the site are not exposed by any source reachable here.
