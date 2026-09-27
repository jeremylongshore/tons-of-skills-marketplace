<!-- doc-class: record -->

# tonsofskills.com Security-Warning Reports: Incident Record

- **Date:** 2026-09-27 (investigation 19:08 to 19:45 UTC)
- **Severity:** P2 (site up and serving worldwide; a subset of visitors behind specific security products or filtering DNS are blocked or shown warnings)
- **Status:** Origin cleared. One infrastructure defect fixed. External reputation remediation prepared and awaiting owner approval (no third-party submissions made).
- **Filing note:** the investigation brief suggested `000-docs/incidents/`. This repo files after-action records flat in `000-docs/` as `NNN-AA-AACR-*` (see 812), so this record follows the repo convention.

## Executive summary

The origin is healthy, uncompromised, and correctly configured for TLS. The warnings come from
**external threat-intelligence classification of the domain `tonsofskills.com`**. Two independent
protective-DNS services currently block the domain as malicious:

| Service | Resolver tested | Answer for tonsofskills.com | What a browser sees |
|---|---|---|---|
| DNS4EU (EU public DNS; threat feed operated by Whalebone) | `86.54.11.1` protective, `.12` child, `.13` ad+protective | sinkhole `51.15.69.11` | HTTPS: certificate for `doh.joindns4.eu`, so a name-mismatch **certificate error**; HTTP: "We have prevented you from accessing potentially malicious website" |
| CIRA Canadian Shield | `149.112.121.20` Protected, `.30` Family | sinkhole `75.2.78.236` / `99.83.179.4` | HTTPS: connection timeout; HTTP: "Malware blocked by CIRA Canadian Shield" |

The same resolvers return the real address for `claudecodeplugins.io`, `intentsolutions.io`,
`jeremylongshore.com` and `startaitools.com`, all of which are on the **same IP**. The block is
therefore a **domain** classification, not an IP reputation problem. Unfiltered tiers of the same
providers (DNS4EU `86.54.11.100`, CIRA Private `.10`) return the correct address, so the answer is
policy, not a DNS fault.

Because the site sends HSTS (`max-age=31536000; includeSubDomains`), a browser that has visited it before
refuses to let the user click through a sinkhole's certificate error. That is the "large warning page
with no way past it" several people described.

## Symptom-by-symptom root cause

| Report | Most likely product class | Proven vs inferred |
|---|---|---|
| Teammate, iPhone Chrome: `ERR_SSL_PROTOCOL_ERROR`, "sent an invalid response", plus "flagging my security apps" and a phone warning | **On-device mobile security app with web protection** (local VPN or DNS filter). When these apps block an HTTPS site they cannot present a valid certificate for it, so they reset the connection or inject non-TLS bytes. Chrome renders that as `ERR_SSL_PROTOCOL_ERROR` "sent an invalid response", while the app raises its own notification. | **Inferred.** The mechanism is consistent. The origin-side causes that would produce this error are ruled out (see TLS findings). No app name or screenshot was available. Likely vendors: Gen Digital (Norton 360, Avast One, AVG), McAfee (also behind Verizon Digital Secure), Lookout (also behind carrier-bundled protection), Bitdefender, Trend Micro, Malwarebytes, T-Mobile Scam Shield. Avast's URL-reputation backend fetched the site on 2026-09-09 (access-log UA `AvastSecureBrowser`, cloud source range). |
| Overseas user: certificate / "security certificate" errors | **Protective DNS resolver** (DNS4EU, or an ISP resolver running the same Whalebone feed) answering with a sinkhole that presents its own certificate | **Mechanism proven** end to end from this investigation (sinkhole returns `CN=doh.joindns4.eu`; `curl` fails with "no alternative certificate subject name matches"). Attribution to this specific user is inferred. |
| Oregon user: "TOS / Terms of Service violation" alert | **Secure web gateway or managed-network filter** (employer, school, or ISP "advanced security") showing an acceptable-use-policy block page | **Inferred and weakest.** No provider (Porkbun, Contabo, Let's Encrypt, Google, Microsoft, Cloudflare) sent any ToS, abuse, suspension or takedown notice (mailbox searched since 2026-08-01). The site has no "violation" wording on its pages. "Acceptable use policy violation" is standard wording on Zscaler, Palo Alto, Fortinet, Cisco Umbrella, Forcepoint and Lightspeed/GoGuardian/Securly block pages. |
| Others: large browser/security warning pages | Mix of the above | Not Google Safe Browsing (status 1, "no unsafe content"), so these are not native Chrome or Safari red-screen phishing warnings. They are either certificate interstitials from sinkholes (proven mechanism) or vendor block pages. |

### Why different users saw different errors

The same classification surfaces differently depending on **where** in the path the blocking product sits:

1. **DNS layer with a TLS-speaking sinkhole** (DNS4EU): a valid certificate for the wrong name produces a certificate error. HSTS removes the bypass.
2. **DNS layer with a sinkhole that does not answer 443** (CIRA): the connection times out, and HTTP shows a "malware blocked" page.
3. **On-device app/VPN**: a connection reset or garbage bytes produces `ERR_SSL_PROTOCOL_ERROR`, plus an app notification.
4. **Managed gateway** (proxy/NGFW): a branded block page appears, often "acceptable use / policy violation", or a certificate error if the device does not trust the gateway's inspection CA.
5. **Unfiltered networks** (40 of 40 global check-host.net nodes, 20 of 22 public resolvers): the site works normally.

## Evidence

All commands were run 2026-09-27 from the dev box, from the VPS (read-only), or from public probes.

### DNS findings

- Apex and `www` A record `167.86.106.29`, no AAAA, no CAA, NS = Porkbun (four `*.ns.porkbun.com`). This matched on every resolver that answered normally.
- A 22-resolver filtering matrix returned the correct IP from Quad9, Cloudflare 1.1.1.2/1.1.1.3, OpenDNS and OpenDNS FamilyShield, AdGuard (default and family), CleanBrowsing (security and family), ControlD (malware and family), Comodo, Yandex (safe and family), UltraDNS (threat and family), SafeDNS, OpenBLD, NextDNS anycast, Surfshark, AliDNS, DNSPod and Google.
- **Blocked:** DNS4EU protective, child and ad+protective (`51.15.69.11`, Scaleway AMS, PTR `*.instances.scw.cloud`), and CIRA Protected and Family (`75.2.78.236`, `99.83.179.4`, AWS Global Accelerator).
- Control domains (`example.com`, `github.com`) resolve normally on all of them. Mullvad and DNSFilter answered REFUSED or a block for everything, including controls, so they were excluded as uninformative.
- The DNS4EU passthrough payload decodes to `{"Host":"tonsofskills.com",...,"SinkholeID":6000063}`.
- check-host.net DNS from global nodes: every node resolved `167.86.106.29`.
- **Defect found:** `www.claudecoworkskills.io` had **no A record**, although Caddy declares it as a redirect host. Fixed; see Changes made.

### TLS findings

- Leaf certificates: apex `CN=tonsofskills.com` (YE2), `www` (YE1). Both are ECDSA P-256, notBefore 2026-09-03, notAfter 2026-12-02. TLS 1.2 and 1.3 only.
- Served chain: `leaf -> YE2 -> Root YE (ISRG) -> ISRG Root X2 (cross-signed by X1)`.
- **Old-trust-store validation** (the main suspect for the certificate errors):
  - CAfile containing **only ISRG Root X1**: `openssl s_client -verify_return_error`, depth 4 = X1, `Verify return code: 0 (ok)`. `curl --cacert x1.pem --capath /nonexistent`: HTTP 200.
  - CAfile containing **only ISRG Root X2**: depth 3 = X2, `0 (ok)`. `curl`: 200.
  - Offline: `openssl verify -CAfile x1.pem -untrusted <served intermediates> leaf.pem` returns OK, and the same with X2.
  - Negative control, a store with only DigiCert Global Root G2: `curl: (60) unable to get local issuer certificate`. The test discriminates.
- **SSL Labs** (full scan): grade **A+**, `chainIssues=0`, trusted in the Mozilla, Apple, Android, Java and Windows root stores; 46/68 client simulations succeed. Every failure is a pre-2016 client (Android 2.3 to 4.3, IE 6 to 10, Java 6/7, Safari 5 to 8, iOS 6 to 8, Chrome 49 on XP) that lacks TLS 1.2 AEAD. This is expected and not relevant to a current iPhone.
- **Conclusion:** the new Let's Encrypt "Gen Y" chain validates for any client that trusts X1 or X2. It is **not** the cause of the certificate reports.
- **Protocol matrix:** TLS 1.0 and 1.1 are refused. TLS 1.2 accepts only ECDHE-ECDSA AES-GCM and ChaCha20. TLS 1.3 uses AES-128-GCM. ALPN is h2. No OCSP staple is sent; Let's Encrypt ended OCSP, so the certificate carries a CRL DP only.
- **No or unknown SNI:** a connection without SNI, with the bare IP as SNI, or with an unknown name gets **TLS alert 80 (internal_error)**. This is Caddy's default when it has no certificate for the name. A client that omits SNI would see `ERR_SSL_PROTOCOL_ERROR`. Every real browser sends SNI, so this is recorded as a mechanism rather than a cause. A trailing-dot SNI (`tonsofskills.com.`) gets alert 50.
- **HTTP/3 defect (latent, not causal):** Caddy advertises `alt-svc: h3` and listens on UDP 443, but the host firewall allows only `443/tcp`. An aioquic handshake to `tonsofskills.com:443/udp` **times out**, while `cloudflare-quic.com` and `www.google.com` succeed from the same client. Browsers race QUIC against TCP and fall back, so users see no error, only an avoidable first-connection delay. This is estate-wide (every Caddy site advertises h3). Not changed during the incident; see Recommended follow-up.
- **Certificate Transparency** (crt.sh): issuers are Google Trust Services (WR3, March to May, the former Firebase hosting) and Let's Encrypt only. The wildcard `*.tonsofskills.com` certificates (R13 2026-03-04, R12 2026-05-16, YR2 2026-07-28) are Porkbun's automatic registrar SSL. The Porkbun API `ssl/retrieve` returns the 2026-07-28 YR2 wildcard with an identical notBefore. **No unexpected issuance.**
- Caddy journal since 2026-09-20: every ACME error (50 "could not get certificate", 24 "job failed") is for `www.claudecoworkskills.io` (`no valid A records found`). No errors for tonsofskills names. Caddy logs TLS handshake failures only at DEBUG, so their absence at INFO is not proof on its own; the external probes above are the evidence.

### Redirect chains (every hop)

| Start | Hops |
|---|---|
| `http://tonsofskills.com/` | 308 to `https://tonsofskills.com/`, then 200 |
| `http://www.tonsofskills.com/` | 308 to `https://www.tonsofskills.com/`, then 200 (www serves content; it does not canonicalize to the apex) |
| `https://claudecodeplugins.io/<path>?q` and `www.` | 301 to `https://tonsofskills.com/<path>?q` |
| `https://claudecodeskills.io/<path>?q` and `www.` | 301 to `https://tonsofskills.com/<path>?q` |
| `https://claudecoworkskills.io/<path>?q` | 301 to `https://tonsofskills.com/<path>?q` |
| `https://www.claudecoworkskills.io/` | **Before:** NXDOMAIN. **After fix:** 301 to `https://tonsofskills.com/` (valid YE2 certificate); `http://` returns 308, then 301, then 200 (2 hops) |

All alias certificates are valid Let's Encrypt certificates with the correct single-name SAN. The
`reverse_proxy https://tonsofskills.com` near Caddyfile line 525 belongs to the **startaitools.com**
site block (its `/api/forms/*` route), not to an alias host.

### Proxy / CDN / container findings

- There is no CDN or proxy in front of the site. DNS points straight at the VPS and Caddy terminates TLS.
- The site is static files served by Caddy's `file_server` from `/srv/tonsofskills/dist`, a symlink to `releases/fd4873c0b-20260927T102137Z` (= `origin/main` HEAD). **No container is in the request path.** `/api/forms/*` proxies to a loopback-only forms service.
- The 1,825 `reverse_proxy` "aborting with incomplete response" warnings since 09-20 belong to other hosts (analytics, jeremylongshore.com, scorecardecho.com) and are client-cancel noise.

### VPS findings / security compromise assessment

Read-only; nothing was changed apart from the DNS record and the reload described under Changes made.

- **Web root:** 4,187 files, all owned by the deploy user, all modified 2026-09-27 at the 04:20 to 04:21 local deploy. No file is newer than the deploy. The file-set diff against the previous release (`d36428c56`) adds exactly one directory, `blog/orphan-site-folder-cleared-twenty-deps-alerts/`, which matches commit `fd4873c0b`.
- **Injected-content scan across 3,710 HTML pages:**
  - External `<script src>` origins are only `analytics.intentsolutions.io` (3,704) and `www.googletagmanager.com` (3,698). No `<iframe>`. No service worker.
  - 25 distinct executable inline scripts, all identifiable site UI: theme, gtag, copy buttons, TOC, FAQ, bookmarks, and the GetTerms loader on the three legal pages.
  - `eval(`, `atob(` and `fromCharCode` occur only inside code samples on security-skill documentation pages.
  - Four `http-equiv="refresh"` pages remain (the 2026-08 filter incident converted most meta-refresh redirects to real 301s).
- **Caddy config:** the live `tonsofskills-security-headers.caddy` is byte-identical to `marketplace/ops/tonsofskills-security-headers.caddy`. `dpkg -V caddy` reports only the conffile as modified; the binary is unmodified.
- **Host:** the firewall exposes only 80/443 (Caddy) publicly; every other listener is loopback or firewalled, confirmed by external TCP probes. SSH is not publicly reachable, and every accepted login in the window used public-key auth from the private admin network. No unexpected accounts, credential-file changes, or scheduled jobs were found. The only `/etc/caddy` changes since 09-20 are deploy-driven redirect-file rotations, plus a Caddyfile edit on 09-24 that predates the reports. Processes with "(deleted)" executables are long-running daemons from before package upgrades. Detailed host evidence is kept in the operator's private incident notes, not in this public record.
- **Verdict: no evidence of compromise.**

### Application findings

- **GetTerms:** `gettermscdn.com` (GetTerms legal-document embeds) has been used on `/terms`, `/privacy` and `/acceptable-use` since 2025-10-16 and was allowlisted in the CSP on 2026-09-02 (#1422). Every filtering resolver tested resolves it normally. It is not new and not implicated.
- **Plausible reputation triggers.** These are inferred; vendors do not disclose reasons.
  - 417 plugin ZIPs plus 17 category bundles and a 22 MB all-in-one ZIP are served from the apex. `security.zip` (383 entries) and `crypto.zip` (627 entries) contain markdown, Python, JSON, YAML and shell templates only (no binaries, exe, apk, dll, ps1 or bat), with executable bits on about 25 scripts each.
  - Eleven pages carry `curl ... | sh` one-liners (third-party installers: ollama, lokalise, sentry, bun, tailscale, audit-harness).
  - Offensive-security vocabulary (exploit 86, malware 15, evasion 8, ransomware 6, phishing 5) and a `penetration-tester` plugin.
  - Crypto wallet/transaction scripts.
  - The domain is young (registered 2026-03-04).
- **Access-log correlation** (2026-09-07 to now):
  - **VirusTotal** URL scans: UA `AppEngine-Google; appid: s~virustotalcloud`, repeatedly from 09-07 through **2026-09-27 14:29:50 UTC** (today). Someone, or a product that auto-submits, has been sending the URL to VirusTotal.
  - Avast URL-reputation fetch on 09-09.
  - Netcraft survey agent on 09-08 and 09-13.
  - Palo Alto Networks Cortex Xpanse scans about daily. That is attack-surface management, not URL categorization.
- **ZIP downloads** per day: 19 to 454, peaking 09-25 and 09-26. No anomaly that points to abuse.

### Domain / IP reputation findings

| Source | Result |
|---|---|
| Google Safe Browsing (transparency report API) | status 1: no unsafe content |
| Spamhaus DBL (queried authoritatively at `[a-e].gns.spamhaus.org`, test point `dbltest.com` answered `127.0.1.2`) | not listed (domain and `claudecodeplugins.io`) |
| Spamhaus ZEN for `167.86.106.29` (test point `127.0.0.2` answered) | not listed |
| URIBL (via Quad9 unfiltered; test point answered `127.0.0.14`) | not listed |
| SURBL multi (test point answered) | not listed |
| Barracuda, SpamCop, SORBS, PSBL (IP) | not listed |
| AlienVault OTX (domain and IP) | 0 pulses |
| OpenPhish feed | 0 hits |
| urlscan.io | 4 historic scans, no malicious verdict |
| check-host.net HTTPS from 40 nodes in 25 countries (AU, AT, BR, BG, CA, CY, DE, HU, IN, ID, IR, IL, IT, JP, KZ, NL, PT, RO, RU, RS, ES, SE, CH, TR, UK, UA, US) | 40/40 HTTP 200 from `167.86.106.29` |
| **DNS4EU / Whalebone** | **blocked as "potentially malicious"** |
| **CIRA Canadian Shield** | **blocked as "malware"** (Protected and Family tiers) |
| VirusTotal | **not checked: no API key** in any SOPS file. Browser: `https://www.virustotal.com/gui/domain/tonsofskills.com` |
| URLhaus / ThreatFox (abuse.ch) | **not checked:** the API now requires an Auth-Key |
| Norton Safe Web, McAfee, Trend Micro, Bitdefender, Kaspersky, Fortinet, Palo Alto PAN-DB, Cisco Talos, Zscaler, Symantec WebPulse, Forcepoint, Check Point, Webroot BrightCloud, Microsoft SmartScreen | **require a browser/CAPTCHA**; listed below for the owner |

## Changes made

1. **Added the missing DNS record** `A www.claudecoworkskills.io -> 167.86.106.29` (TTL 600) at Porkbun, using `intent-os/ops/dns/porkbun-update-record.sh`. This was already filed as finding `dns-registrar-tls-3` (P2) in intent-os `000-docs/216`.
   - Before-state captured: the zone had apex A, NS and TXT records, and no `www` record. Its sibling zones `claudecodeplugins.io` and `claudecodeskills.io` both carry a `www` A record to the same IP.
   - Rollback: `porkbun-update-record.sh claudecoworkskills.io delete A www ''`.
2. **Triggered issuance with a graceful reload:** `caddy validate` returned "Valid configuration", then `systemctl reload caddy` (unit uses `caddy reload --force`; **no restart**). Caddy obtained the certificate at 19:30:15 UTC. The config file itself was not modified.
3. **No change** to TLS, headers, firewall, site content or caches.

## Verification results

- `www.claudecoworkskills.io` resolves on 1.1.1.1, 8.8.8.8 and 9.9.9.9. Its certificate is `CN=www.claudecoworkskills.io` (YE2), notAfter 2026-12-26, `Verify return code: 0`, and it redirects 301 to `https://tonsofskills.com/`.
- The canonical and other alias hosts were re-checked after the reload: `tonsofskills.com` 200, `www.tonsofskills.com` 200, `claudecodeplugins.io` 301. The ACME failure loop is ended, which stops the burn of Let's Encrypt and ZeroSSL failed-validation quota.
- The reputation blocks are **not** fixed by any origin change. They clear only when DNS4EU/Whalebone and CIRA (and whichever mobile-security vendor flagged the teammate) reclassify the domain.

## Remaining risks

- The domain stays blocked for DNS4EU-, Whalebone- and CIRA-protected users, and probably for some mobile-security and enterprise-gateway users, until each vendor reclassifies it. Feeds cross-pollinate (VirusTotal engines, shared threat feeds), so further vendors may follow while the triggers remain.
- VirusTotal scans are ongoing. A single engine detection there propagates widely, and the current verdict is unknown.
- The HTTP/3 advertisement is unreachable estate-wide (latent latency cost; some middleboxes log it as blocked QUIC).
- SNI-less clients get alert 80 (Caddy default). This matters only if a proxy strips SNI.
- `www.tonsofskills.com` serves a duplicate of the site instead of 301-ing to the apex. Canonical tags mitigate the SEO side, but it doubles the surface that reputation systems see.

## Monitoring (specified; extends the existing collector, no new alerting system)

The estate already runs `intent-os/ops/observability/outside-in-collector.sh once` every 2 minutes on
the dev box. It is live: the liveness `.ok` marker was fresh at the time of writing, and it routes
through the governed `af_dispatch` alert floor, which is Slack-only. **tonsofskills.com is not
currently probed.**

The specification below extends that collector, as a change in intent-os with registry controls
(owner and runbook required), under the repo's normal CI gates:

1. **PROBES rows, `http` kind:**
   - `https://tonsofskills.com/`
   - `https://www.tonsofskills.com/`
   - `https://claudecodeplugins.io/` (expect `301` with Location `https://tonsofskills.com/`)
   - the same for `www.claudecodeplugins.io`, `claudecodeskills.io`, `www.claudecodeskills.io`, `claudecoworkskills.io` and `www.claudecoworkskills.io`

   The redirect rows need a new `redirect` kind: expected state = status 301 plus the Location prefix.
2. **`tls-chain` kind:** `openssl s_client -servername H -CAfile <ISRG Root X1 only> -CApath /nonexistent -verify_return_error` plus a days-to-expiry check. Healthy = verify 0 and more than 21 days left. This catches a chain regression for X1-only clients and a stalled renewal.
3. **`dns-drift` kind:** `dig +short A/AAAA/NS` for the apex and `www`. Expected = A `167.86.106.29`, no AAAA, NS `*.ns.porkbun.com`.
4. **`reputation` kind, hourly (not every 2 minutes):**
   - Resolve the apex via DNS4EU `86.54.11.1`, CIRA `149.112.121.20`, Quad9 `9.9.9.9`, Cloudflare `1.1.1.2` and OpenDNS FamilyShield `208.67.222.123`. Healthy = every answer is `167.86.106.29`, and a control domain resolves normally on the same resolver, so a resolver outage reads as `collection_failed`, not `failed`.
   - Plus Spamhaus DBL queried authoritatively (`@a.gns.spamhaus.org`, gated on the `dbltest.com` test point) and SURBL (gated on `test.surbl.org`).
   - Plus Google Safe Browsing status from the transparency API.

   Severity `high`, 1-strike (reputation changes are not flaps). Right now this control would read **failed**; ship it with that as the known baseline so the recovery is observed.
5. **Content integrity (optional):** the probe fetches `/` and asserts that the only external `<script src>` origins are `analytics.intentsolutions.io` and `www.googletagmanager.com`.

## Recommended follow-up

**Owner approval required. Nothing below has been submitted.**

1. **False-positive / recategorization submissions** (prepare with the text below):
   - DNS4EU / Whalebone: `https://joindns4.eu/for-public` (the "More information" link on the block page). Cite sinkhole ID `6000063`.
   - CIRA Canadian Shield: `https://www.cira.ca/en/why-am-i-seeing-block-page/` (report a false positive).
   - VirusTotal: open `https://www.virustotal.com/gui/domain/tonsofskills.com` and `/gui/url/...` for `https://tonsofskills.com/`. Request a rescan and record which engines flag it, then file with each flagging engine.
   - Gen Digital (Norton, Avast, AVG): `https://safeweb.norton.com/report?url=tonsofskills.com` and `https://www.avast.com/false-positive-file-form.php` (website option).
   - McAfee: `https://sitelookup.mcafee.com/`
   - Trend Micro: `https://global.sitesafety.trendmicro.com/`
   - Bitdefender: `https://www.bitdefender.com/consumer/support/answer/29358/`
   - Lookout: via Lookout support (web-protection false positive)
   - Kaspersky: `https://opentip.kaspersky.com/tonsofskills.com`
   - ESET: `https://support.eset.com/en/kb141`
   - Sophos: `https://support.sophos.com/support/s/filesubmission`
   - Microsoft SmartScreen: `https://www.microsoft.com/en-us/wdsi/filesubmission` (URL, incorrectly detected)
   - Fortinet: `https://www.fortiguard.com/faq/wfratingsubmit`
   - Palo Alto: `https://urlfiltering.paloaltonetworks.com/`
   - Cisco Talos / Umbrella: `https://talosintelligence.com/reputation_center/lookup?search=tonsofskills.com`
   - Zscaler: `https://sitereview.zscaler.com/`
   - Symantec WebPulse: `https://sitereview.bluecoat.com/`
   - Forcepoint: `https://csi.forcepoint.com/`
   - Check Point: `https://usercenter.checkpoint.com/ucapps/urlcat/`
   - Webroot BrightCloud: `https://www.brightcloud.com/tools/url-ip-lookup.php`
   - Cloudflare Radar: `https://radar.cloudflare.com/domains/feedback/tonsofskills.com`
   - Suggested category for all of them: *Information Technology / Software Development*.
   - Suggested text: "tonsofskills.com is the public catalog for the open-source Claude Code plugin marketplace (github.com/jeremylongshore/tons-of-skills-marketplace), operated by intentsolutions.io LLC. Downloads are source-only plugin bundles (Markdown, Python, JSON, YAML, shell templates; no binaries). Security-related plugins are defensive tooling documentation. Google Safe Browsing, Spamhaus DBL, SURBL, URIBL and OTX report it clean."
2. **Trigger-surface reduction.** These are **product decisions**, proposed and not shipped. Ordered by expected effect:
   - (a) Move the ZIP bundles off the apex, to GitHub Releases or a separate download domain, so a file-level detection cannot taint the catalog domain.
   - (b) Replace inline third-party `curl ... | sh` one-liners with links to each vendor's own install page.
   - (c) Put offensive-security and crypto-wallet plugin pages behind a clear "defensive/educational" framing and keep raw script bodies out of the HTML.
   - (d) 301 `www.tonsofskills.com` to the apex.
3. **HTTP/3:** decide between allowing `443/udp` in the VPS firewall (h3 then works; this adds the QUIC stack to the public attack surface) and disabling h3 advertisement in Caddy's global `servers { protocols h1 h2 }`. It is estate-wide either way; land it in the intent-os ingress/host source of truth.
4. **Optional:** `default_sni tonsofskills.com` in the Caddy global options, so SNI-less clients receive a valid certificate instead of alert 80. Low value; do it only if a report ever implicates an SNI-stripping proxy.
5. **Implement the monitoring spec above** in intent-os.
6. **Questions for the reporting users,** if they become reachable:
   - Which security app, VPN, or antivirus is installed (exact name)? Is it a carrier bundle?
   - A screenshot of the warning, including the full URL bar and any vendor logo.
   - Network at the time (home Wi-Fi, cellular, work, school, public Wi-Fi), ISP or carrier, and country.
   - Does the site load with the app's web protection or VPN switched off, or on cellular versus Wi-Fi?
   - Did they type `tonsofskills.com` or follow a link (which link, from where)?
   - For the "TOS violation" report: the exact wording and whose branding was on the page (employer, school, ISP, or the app).
