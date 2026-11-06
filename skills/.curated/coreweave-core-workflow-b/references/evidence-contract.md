# Evidence contract: Distributed training recovery review

Community-contributed; not affiliated with CoreWeave.

Input includes `world_size`, one `workers` entry per process rank with rank/rendezvous/gpu_count/transport, `model_revision`, and `checkpoint` recovery evidence. Record transport from positive data-path logs, not bootstrap traffic. The helper assumes one declared GPU allocation per supplied process description; inventory from scheduler assignment must substantiate it. A shared rendezvous address is necessary but does not prove network reachability. A restore_test_passed flag records a supplied recovery result; the helper does not load a checkpoint or launch training. Use the fabric diagnostic for raw NCCL logs.

## Input and review boundary

The packaged `tests/fixtures/example.json` is the complete normalized input example.
`cases.json` includes specific negative outcomes as well as stale, wrong-scope and
injected-instruction variants. Inputs are supplied observations, not authenticated
proof. Review the source of every boolean assertion. The common envelope records
intended and observed scope plus a timezone-aware capture timestamp. Output includes
the SHA-256 of the actual bytes read, never a token or raw log excerpt.

Read-only collection commands and upload/deploy commands belong to the human-approved
operator workflow. Helper parsing is intentionally independent of credentials and
network availability. Unknown nested platform formats fail closed; add a reviewed
fixture before extending an adapter.

## Source and review

Primary source: https://docs.pytorch.org/docs/stable/distributed.html

Contract reviewed 2026-11-05. Repository examples are original. Vendor version and
account-specific availability must be confirmed separately; no live operation was
performed for this pack. See the blueprint for requirements and release boundaries.
