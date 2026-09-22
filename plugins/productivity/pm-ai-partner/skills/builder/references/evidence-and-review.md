# Builder Evidence and Review Checklist

Use this checklist when the requested implementation depends on an existing repository or will be
maintained after the first demonstration.

1. Use `Glob` to identify the smallest relevant file set, `Grep` to trace existing conventions,
   and `Read` to inspect the governing files before proposing an implementation.
2. State the user, outcome, lifetime, constraints, and acceptance checks. Distinguish a one-off
   prototype from a maintained tool.
3. Use `Write` only for genuinely new files and `Edit` for targeted changes. Preserve unrelated
   content and follow repository instructions.
4. Run only the declared scoped `Bash(npm:*)` or `Bash(node:*)` commands when the project already
   uses those runtimes. Do not install packages or run generated code without confirming scope.
5. Verify the happy path, one realistic failure path, and the exact files changed. Report what was
   tested, what was not tested, and any operational follow-up.

Reject a solution that hides configuration, hard-codes secrets, silently overwrites files, or
claims production readiness from a visual demonstration alone.
