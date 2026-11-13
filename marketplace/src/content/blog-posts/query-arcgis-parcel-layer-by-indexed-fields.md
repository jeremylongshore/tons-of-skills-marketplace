---
title: "ArcGIS FeatureServer Query Slow: Use Indexed Fields"
description: "Florida's ArcGIS parcel layer answers in under a second on county number and owner name. Address queries took 35 to 55 seconds or failed."
date: "2026-11-10"
tags: ["python", "automation", "debugging", "gis", "data-engineering"]
featured: false
canonical: "https://startaitools.com/posts/query-arcgis-parcel-layer-by-indexed-fields/"
---
Querying a public parcel layer by the obvious field is the slow path. Florida's statewide parcel layer, an ArcGIS FeatureServer (a map service that serves its records through a REST query URL), took 35 to 55 seconds per address query, timed out, or returned HTTP 400. This note covers the two fields the layer indexes, the service's own county numbers (Escambia is 27, not the 17 an early county filter used), and the per-row verdict (verified, mismatch or hold) you can run before paying for anything.

The stakes are downstream. The lead records came from a data vendor. Before a record went to skip-tracing (a paid lookup for current contact details) or to a mailing vendor, the plan was to check the owner against free county records. That check only works if it is fast enough to run on every row. As first written, it was not, and the easy path was to skip it.

## What the layer indexes

The layer answers quickly on two fields: CO_NO (county number) and OWN_NAME (owner name). The pull request that added the check records 35 to 55 seconds per address query, or a timeout. Two address probes and one background run from the session sat at or just past the top of that range:

- Address query with a zip filter (PHY_ZIPCD=32507): 55.1 seconds, then HTTP 400 "Invalid query parameters."
- City-name query: 55.2 seconds, same 400.
- A background run of the address script passed a 600 second command timeout and was stopped.

The owner-name path, by contrast, returned 200 rows in 0.9 seconds.

Fast is not the same as right. That 200-row owner-name result came back under county 11, and its PHY_ZIPCD values were the placeholder '99999'. None matched the lead's zip.

## County numbers are the service's own

The layer's CO_NO is not a FIPS code (the federal county numbering standard). It numbers counties alphabetically from 11, so Escambia County is 27. The first county filter used 17. A count query on CO_NO=17 counted 11,616 rows in 0.1 seconds, and a sample showed they belonged to another county.

The handler maps zip codes to county numbers with a plain dictionary:

```python
FL_COUNTY = {"32506": 27, "32507": 27}  # Escambia
```

A zip missing from that map gets None as its county, and the handler returns no_parcel_match with the reason "zip outside configured FL counties". In the counts, an unmapped zip looks the same as a real miss, so the map has to cover every zip you pull.

## Query the indexed fields, then filter in code

The Florida query asks the service for one thing: rows in the county whose owner name starts with a token. The handler does the rest in Python. A row counts as a hit only if:

- Zip: the first five digits match the lead's.
- House number: equal to the lead's.
- Street words: after normalizing suffixes (STREET to ST, BOULEVARD to BLVD) and dropping unit words such as UNIT, APT, STE, LOT and BLDG, at least two words must be shared (one, if the lead's street has only one word).

A single owner-name word can be a common one, so the handler tries up to four words, longest first, and stops at the first hit:

```python
for t in sorted(own, key=len, reverse=True)[:4]:  # keep trying: first token can be a common word
    ...  # query CO_NO plus OWN_NAME LIKE 't%', filter locally, break on the first hit
```

Interim, with the right county and a single owner-name word per lead, the run verified 13 of 20: Alabama 8 of 8 and Florida 5 of 12. Each Florida lookup on county plus owner name took under a second. The seven Florida misses were suspected to come from owner-name formatting, trusts and LLCs, or sales that happened after the roll was built. That was a suspicion, not a finding. Trying several tokens took verified rows to 16 of 20.

Final numbers:

- Florida: 8 verified, 1 mailing_mismatch, 3 no_parcel_match
- Alabama: 8 verified
- 4 rows held from mail (the mailing_mismatch and the three no_parcel_match rows): the rule is that nothing short of verified gets mailed

## Baldwin County has no API

Baldwin County, Alabama, publishes no API. The handler GETs the Revenue Commission's public property search page, pulls the __RequestVerificationToken from its form, and POSTs the address search with an X-Requested-With header. It then parses the JSON rows array that the results grid is built from. Probing the county's ArcGIS service roots first returned an empty services list and a 404. The handler searches one Alabama row at a time, with a 1.5 second pause between searches.

Two free extras came out of the lookups. Alabama owners had a tax balance due on 5 of 8 rows. Florida rows carry a homestead flag, a just value and a last sale year, and the homestead flag was set on 2 of the 8 verified Florida rows.

## Verdicts decide what gets paid for

Every row gets one verdict:

- verified: the owner of record matches, and for Florida the mailing address matches too
- mailing_mismatch
- owner_mismatch
- no_parcel_match: hold, do not mail until resolved
- error: recorded against that row only

The handler itself labels only no_parcel_match as a hold; holding the other non-verified verdicts is the mailing rule on top of it. One bad row never stops the batch. A new output file is created with mode 0600, and stdout prints counts only, not records.

## What is still open

Both public sources can change under you: the Florida layer is a JSON API, the Baldwin search is an HTML form. On the Baldwin side the only deliberate raise is a missing verification token. Network errors and malformed grid JSON also raise, and all of them land as per-row error verdicts. But if the grid's rows array disappears or its address field is renamed, the lead reads as no_parcel_match: a silent hold, not a loud failure. A renamed owner field would show up as owner_mismatch instead. That is the gap to watch. The verifier is read-only against both sources.

Three unmatched Florida rows still need an address-path fallback or a manual lookup. The clerk's lis pendens check (a court notice that a lawsuit touches the property) is not in yet. Owner names with punctuation match worse than they should. Normalization turns every character outside A to Z, 0 to 9 and space into a space, so the quote never reaches the query, but O'BRIEN becomes the token BRIEN (the one-letter O is dropped), and a prefix match on BRIEN never hits a name stored as O'BRIEN. The handler then depends on another token in the name to find the row.

## How the session got there

The session ran on Claude Fable 5.1 and Claude Opus 5.5. Its first pass queried Florida by address and zip. Each probe took about 55 seconds and came back as HTTP 400, and one background run passed the 600 second command timeout and was stopped. The first owner-name query was fast but useless: its rows came back from county 11 with placeholder zips. The next attempt filtered on county 17, which was also the wrong county. When the operator asked why it took so long, the model gave two causes: the layer only indexes county number and owner name, and the county code was wrong.

## Use this

- Time one address query against https://services9.arcgis.com/Gh9awoU677aKree0/arcgis/rest/services/Florida_Statewide_Cadastral/FeatureServer/0/query before you build a pipeline on it. Here it took 55 seconds and returned HTTP 400.
- Map your county to the service's own CO_NO value, not FIPS. Run a count query to confirm the number, and check that the rows belong to your county before you trust any hit. Escambia is 27 here.
- Filter on county plus owner-name prefix, match zip, house number and street in your own code, and gate every paid step on a per-row verdict. Hold anything that is not verified.

## Related Posts

- [Confirm Discord webhook delivery with ?wait=true](https://startaitools.com/posts/discord-webhook-wait-true-confirm-delivery/)
- [A dead socket is not a dead host](https://startaitools.com/posts/a-dead-socket-is-not-a-dead-host/)
