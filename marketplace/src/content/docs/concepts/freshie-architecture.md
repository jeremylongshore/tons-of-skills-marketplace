---
title: 'Freshie Inventory Architecture'
description: 'How Freshie uses stock SQLite for its local runtime, full Dolt for versioned history, and DoltHub for public inventory snapshots. The former DoltLite experiment is retired.'
section: 'concepts'
order: 6
keywords:
  - 'Freshie'
  - 'SQLite'
  - 'Dolt'
  - 'DoltHub'
  - 'DoltLite'
  - 'inventory history'
relatedDocs:
  - 'guides/publish-to-marketplace'
  - 'ecosystem/marketplace-overview'
---

## Production storage

Freshie's inventory tools run against **stock SQLite**. Approved, completed inventory snapshots are exported to **full Dolt**, and that versioned history is published to **DoltHub**.

| Layer     | Role                                                                                          |
| --------- | --------------------------------------------------------------------------------------------- |
| SQLite    | Local runtime database used by inventory and validation tools.                                |
| Full Dolt | Versioned system of record, with a commit and a `run-N` tag for each published inventory run. |
| DoltHub   | Public, durable copy of the approved inventory history.                                       |

These layers have different jobs. Publishing a snapshot to DoltHub does not replace the local SQLite runtime with a different database engine. Only the tables approved by the export allowlist enter the public history.

The Astro marketplace serves static pages and generated repository projections. Visitor requests do not query the local Freshie database.

## DoltLite is not the production backend

The former DoltLite experiment is retired and has no active Freshie publisher. Its implementation remains recoverable in Git history. It is not the runtime database, the full Dolt history repository, or the public DoltHub service.

## Reviewing inventory history

Use the [public DoltHub repository](https://www.dolthub.com/repositories/jeremylongshore/freshie-inventory) to inspect published tables and run history. A `run-N` tag identifies a versioned snapshot; it is not a claim that every skill in that snapshot has passed behavioral or native-harness evaluation.

Tracked grade exports are projections of the inventory pipeline. A source change, a static validator grade, a published snapshot, and retained behavioral evidence are distinct records. Check the relevant evidence before making a quality or installation claim.

## Contributor boundary

Contributors submit source changes through the [marketplace publishing workflow](/docs/guides/publish-to-marketplace/). Inventory discovery, grading, export, and publication remain governed operations; this page is not an instruction to create or overwrite a database in an arbitrary checkout.

## Operational source of truth

This guide summarizes the [canonical Freshie operational README](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/freshie/README.md), including its storage roles, export allowlist, and retired DoltLite lane. Follow that document for operational commands, publication ownership, and recovery procedures.
