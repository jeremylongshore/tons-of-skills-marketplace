---
title: "Referrer-Policy same-origin: Django CSRF 403 Origin null"
description: "Referrer-Policy no-referrer makes browsers send Origin: null on same-site form posts, so Django CSRF returns 403. Use same-origin and drop Referer from logs."
date: "2026-10-29"
tags: ["django", "security", "debugging", "testing", "web-development"]
featured: false
canonical: "https://startaitools.com/posts/referrer-policy-no-referrer-origin-null-csrf-403/"
---
A strict Referrer-Policy header can make every real visitor's form post fail with a 403 while your test suite stays green. This post covers why that happens, which header value avoids it, and the access-log leak that the safe value opens up.

The app is a Django access-request site. It mails each applicant a one-time link, and the link opens a token page where the applicant confirms the request, finishes setup or withdraws. The token sits in the page URL, so the Referer header matters here.

## What broke

The site-wide policy was `no-referrer`. The reasoning was sound. No page needs to tell another site where a visitor came from, and a one-time link's token should never reach a third party through a header.

A live browser canary against production was refused at the request form with a 403. Here, a canary is a scripted browser that walks one real user journey on the deployed site. The site owner wanted that test before the first applicants were let in, because the existing browser checks run in-process against the test client and never touch the deployed site.

The proxy log showed the POST carried `Origin: null`. Under `no-referrer`, Chromium serializes the origin of the page's own form submission as null. Django's cross-site request forgery (CSRF) origin check refuses a null origin. Every real person's form post would have failed, starting with the request form and the confirm button.

The test client and the in-process browser check never send an Origin header. The suite was green, and nothing in it could have produced this failure.

The canary had its own failures around that one. The first run never reached the submit button. Django renders labels as "Name:", so an exact label match found nothing, and the Chromium build Playwright expected was not installed. The 403 came on the second run. After the policy fix, a run raised "can't compare offset-naive and offset-aware datetimes" on the mail Date header. A later run waited for a verification mail that a repeat submission never sends. The first run after those fixes passed every step.

The work ran in Claude Code sessions with Claude Opus 5.5. The model wrote the canary, ran it, and read the trace and the proxy log after each failed run.

## The fix

Exempting the form from CSRF would weaken the check. So would trusting a null origin. Changing the policy does not, and this change uses `same-origin`. It keeps the referrer, and with it any token in the page URL, away from every other site. That is why `no-referrer` was chosen in the first place. It also lets the browser name this site as the origin, so the form post carries a real one.

The value changed in three places: the Django setting, the middleware on the private token paths (which also sets no-store caching), and the generated Caddyfiles for staging and production.

```python
SECURE_REFERRER_POLICY = "same-origin"
```

The regression test replays the failure. It posts with the null origin and expects a 403, then posts with the real origin and expects anything but a 403:

```python
refused = client.post(FORM, base, HTTP_ORIGIN="null", secure=True)
assert refused.status_code == 403
accepted = client.post(FORM, base, HTTP_ORIGIN="https://testserver", secure=True)
assert accepted.status_code != 403
```

A second test pins the policy on the request form and the three token pages. Only the regression test above replays the Origin header, and only the live canary shows a real browser sending it, so keep the canary in the loop.

## The leak the safe value opened

With `same-origin`, the browser sends the full page URL as the Referer of every same-origin request. That includes the confirmation POST and the page's asset requests. On a token page, that header carries `https://<host>/confirm/<token>/`.

The access log already redacted the token in the request URI. It did not touch headers. The production proxy log then held one line with an unredacted 80-character token in `request>headers>Referer`. It came from the live canary's confirmation at 01:54 UTC on 2026-10-30 (the evening of the 29th at UTC-06:00). The token was single-use, and that same request consumed it, so it could not be replayed. It still sat in a log file.

The fix is to delete the header in the log filter. The Caddy log format gets one more directive beside the URI redaction: `request>headers>Referer delete`. A second regular expression was the other option. A delete wins because the log never needs the Referer, and a delete cannot miss an encoding variant.

Verification: ruff came back clean, and the staging proxy and acceptance tests passed, 39 in 65.28 seconds.

## What it cost

The fix took two CI fix-up commits on the same PR. The regression test used a fixture person name that was not on the personal-data scan's list. The test module also had to import a mapped package for the test-selection map. The CI log viewer hid the failure details, so the raw CI log had to be read.

The price was those fix-up commits, plus one single-use token that reached a log file before the filter was changed.

## Use this

- Set Referrer-Policy to `same-origin` on any site whose forms check Origin, and submit one real form in a real browser before you go live.
- Add a regression test that posts with `HTTP_ORIGIN="null"` and expects a 403, plus a post with the real origin that does not.
- Delete the Referer header in your access-log filter on any page that carries one-time tokens, then grep the existing log for tokens. The code is at https://github.com/intent-solutions-io/catalyst-onboarding-v2.

## Related Posts

- [Locked out of a free course](https://startaitools.com/posts/locked-out-of-a-free-course/): a green test client next to a page that was broken for real users.
- [SMTP 250 is not delivery](https://startaitools.com/posts/smtp-250-not-delivery-three-receipts/): an accepted send does not prove the confirmation mail arrived.
