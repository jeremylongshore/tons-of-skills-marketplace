# Technical Analysis Evidence and Review Checklist

Use this checklist when translating a repository or system into product implications.

1. Use `Glob` to map relevant files, `Grep` to trace entry points and symbols, and `Read` to inspect
   implementations, tests, configuration, and documentation.
2. Distinguish documented intent from observed implementation. Cite exact local paths or supplied
   sources for material claims.
3. Trace one representative path from input through state changes, dependencies, output, and
   failure handling. Note platform or environment variants.
4. Translate the behavior into user impact, operational risk, product constraints, and questions
   that require engineering confirmation.
5. Report confidence, uninspected areas, contradictory evidence, and a reproducible next check.

Do not infer runtime behavior from names alone, quote stale documentation as current code behavior,
or claim completeness when key dependencies or environments were unavailable.
