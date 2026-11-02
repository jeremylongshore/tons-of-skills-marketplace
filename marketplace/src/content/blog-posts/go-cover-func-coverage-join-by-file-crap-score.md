---
title: "go tool cover -func: Join Coverage by Function, Not by File"
description: "Join go tool cover -func output to complexity by file, line and function. Keyed by file, each function inherits the last one's coverage and can pass CRAP."
date: "2026-10-27"
tags: ["testing", "ci-cd", "debugging", "automation"]
featured: false
canonical: "https://startaitools.com/posts/go-cover-func-coverage-join-by-file-crap-score/"
---
A CRAP-score gate can pass a Go function that no test runs. The gate matched coverage to complexity by file path alone, so every function in a file inherited the coverage of the last function in that file. This post covers that join, the test that pins it, and a second gap where a missing complexity tool left zero functions to score, which could pass. By the end you will know whether your scorer has the same join and how to rekey it.

## The formula

A CRAP score is a per-function number built from complexity (the count of independent paths through a function) and coverage (the share of its statements the tests execute). The intent-audit-harness package, an in-repo set of deterministic test-quality checks, computes it as `(complexity ** 2) * ((1.0 - cov) ** 3) + complexity`, with coverage as a fraction. A function with complexity 6 and 0% coverage scores 42. At 100% it scores 6. Its default production per-function threshold is 30, so the first fails and the second passes. The number only means something when the coverage belongs to the same function.

## The join

`go tool cover -func` prints one line per function, holding its file and line, its name and its percentage. The old scorer reduced each line to its file and stored the percentage like this:

```python
coverage[fpath] = pct
```

Each line overwrote the one before it. When the loop ended, every file held one number, the percentage of its last function, and the lookup `coverage.get(fpath, 0.0)` gave that number to every complexity row in the file.

## The regression test

The regression test stubs `gocyclo` and `go tool cover -func` output for a `src/main.go` with two functions. `Risk` starts at line 1 with complexity 6 and 0.0% coverage. `Fine` starts at line 10 with complexity 1 and 100.0% coverage. The test asserts that `Risk` gets 0 and scores above 30. Under the old join, `Risk` took 100 from `Fine`, so its score was 6 and it passed. Because both tools are stubbed, it runs without Go installed. The PR description reports, from an unpublished local log, that this case failed before the fix.

## Check your own scorer

Suppose a file holds `ParseConfig` (complexity 12, 0% coverage) followed by `Name` (complexity 1, 100% coverage). This example is hypothetical. Under a file-only join, `ParseConfig` takes 100% from `Name` and scores 12, under the threshold of 30, so it passes. Run a file shaped like that through your scorer. If `ParseConfig` reports 100% coverage, or a CRAP score under 30, your join is keyed by file.

## Key on the declaration line

The fix keys each coverage entry on three values:

```python
key = (fpath, line_number, parts[1])
```

The location is split on its last colon, so the number is the function's declaration line. Name alone is not enough. A second fixture has two methods both named `Risk` in one file, a value receiver at line 5 and a pointer receiver at line 6. Its Go output is real `go tool cover -func` output from Go 1.27.3, captured offline. Its complexity rows are hand-written. Keyed by name, the two methods would collide. Keyed with the line, they stay separate.

## The empty list

The empty list was the second gap. Before the change, a missing `gocyclo` printed a notice and returned an empty list. With zero methods there was nothing to fail, so the gate could exit clean. Now the scorer raises a `MeasurementError`, which the gate reports as ADVISORY with exit 2. The coverage step had a related gap: its exit code was ignored, so a failed reader looked like a successful one. It now raises. In read-only mode the scorer also no longer runs `go test` to create a missing coverage file.

## Three outcomes

The change makes three outcomes explicit. PASS (exit 0) needs every requested partition to have candidate files, and each file to have usable method measurements, with thresholds holding. FAIL (exit 1) means a measured method, or a complete production average, exceeds an unchanged threshold. ADVISORY (exit 2) covers a collector that is missing, failed or malformed; a run that scored zero methods; a candidate file without method evidence; and a requested partition that holds zero source files. Exit 2 used to mean only an unsupported language. Anything that read it that way now has to inspect the metadata.

## Where it stands

PR #227 is open and held. The change alters verdicts, stdout and exit codes, so it needs a major version at source landing, and the branch keeps package versions at 1.5.1 on purpose. Hosted CI at b06dc2d (run 40462536747) completed successfully, and the public CRAP job reports six old tests and sixteen new ones. The configured MiniMax review run ended cancelled for both jobs. That is not an approval. Nothing here is merged or released.

## Use this

- Run a two-function file through your scorer, complex untested function first and tested function last. If the untested one reports 100%, rekey coverage on file, declaration line and function name.
- Make every missing or failing measurement return an advisory result, never an empty list. Test it by hiding the complexity tool from `PATH` and asserting the result is not PASS.
- Read the fix in [PR #227](https://github.com/jeremylongshore/intent-audit-harness/pull/227) before you copy it. It is open and held for a major version, so treat it as a reference, not a dependency.

## Related Posts

- [Grep exit 2 means it could not search](https://startaitools.com/posts/grep-exit-code-2-ci-scan-reports-clean/): another case of missing evidence read as a pass.
- [A freshness gate that accepts the wrong mode flag and still exits green](https://startaitools.com/posts/wrong-mode-green-is-not-a-gate/).
- [Why the gates ship inside each repo as a versioned dependency](https://startaitools.com/posts/audit-harness-v010-enforcement-travels-with-code/).
