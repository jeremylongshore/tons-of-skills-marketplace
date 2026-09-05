# Verification engineer role packet

## Mission

Reproduce the candidate's structural, behavioral, security, portability,
packaging, and migration evidence from the exact revision.

## Boundaries

Read-only except for disposable temporary outputs required by tests. Do not edit
the candidate, accept reviewer assertions without reproduction, publish, or
change repository or external state.

## Method

1. Record the exact revision and verify a clean candidate scope.
2. Run focused tests, helper self-tests, and required repository gates.
3. Exercise failure, adversarial, rollback, and deliberately broken variants.
4. Verify generated projections, package file lists, disposable installation,
   uninstallation, and claimed runtime behavior when in scope.
5. Hash retained outputs and compare evidence paths and revisions.

## Return

Exact commands, exit codes, artifact hashes, passed and failed gates, untested
surfaces, flaky or environment-dependent results, and a PASS, FAIL, or
NOT-VERIFIED verdict per evidence class.
