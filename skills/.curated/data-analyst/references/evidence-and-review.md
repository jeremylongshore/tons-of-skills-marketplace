# Data Analysis Evidence and Review Checklist

Use this checklist before reporting a metric, comparison, or causal interpretation.

1. Use `Glob` to locate schemas and data notes, `Grep` to trace metric definitions, and `Read` to
   inspect the authoritative query or documentation.
2. Define the unit of analysis, population, time window, exclusions, and denominator before
   calculating a result.
3. Keep raw observations, transformations, and interpretation separate. Show the query or formula
   when the user can safely reproduce it.
4. Check missingness, duplicate records, timezone boundaries, sample size, seasonality, and
   selection effects. Treat correlation as non-causal unless the design supports causality.
5. Report the result, uncertainty, decision implication, and one validation or sensitivity check.

Use only the user's existing authenticated data environment. Never request, print, or embed
credentials. If authentication is unavailable, stop at a reproducible query plan and explain the
required access without inventing results.
