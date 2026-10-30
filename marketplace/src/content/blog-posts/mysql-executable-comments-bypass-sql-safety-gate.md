---
title: "MySQL Executable Comments Bypassed Our SQL Safety Gate"
description: "MySQL and MariaDB run executable comments as code, so a SQL guard that strips comments before classifying can be bypassed by those comments. Three blind spots."
date: "2026-10-25"
tags: ["testing", "debugging", "architecture", "claude-code"]
featured: false
canonical: "https://startaitools.com/posts/mysql-executable-comments-bypass-sql-safety-gate/"
---
A SQL guard that strips comments before it classifies a statement can be bypassed by the very comments it strips. MySQL and MariaDB execute the contents of a `/*! ... */` block (a comment the server still runs, with a version number attached), and `/*M! ... */` is the MariaDB form of the same thing. The stripping that hides a verb from the scanner also hides it from the reader. By the end of this note you will have three blind spots to hunt for in any text-scanning SQL filter.

The gate in question is `scripts/sql_classifier.py`, part of a plugin I maintain that gives an AI coding agent version-controlled access to a database. It is a stateless classifier, and it is the one place where the plugin decides whether a statement may run. It sorts every statement into one of three classes before the statement is allowed to run. The three classes are a read, a write that version control can undo, and a write it cannot undo at all. If it cannot prove that a statement only reads, the statement is treated as at least a write, so an unrecognized statement never passes as harmless. A multi-statement batch is classified at the severity of its most dangerous statement.

It had just been tightened to refuse `PREPARE`, `EXECUTE`, and `EXPLAIN ANALYZE`. A prepared statement can hide a write behind a name that looks like a read, and `EXPLAIN ANALYZE` runs its subject rather than only planning it. Refusing those three in that one place meant the same rule held everywhere the plugin enforced it, even when the operator had explicitly allowed writes.

Then a final review of the next change reproduced three ways to put those same verbs past the scanner anyway. All three live in the scanner's own text handling, in the two functions that do the unglamorous work: comment stripping and statement splitting.

## Blind spot one: the executable comment

Under MySQL and MariaDB, `/*! ... */` and `/*M! ... */` are executable comments, not annotations. The `/*!80000 ... */` form carries a version number. The scanner treated all of them like any other block comment. Remove the text, leave a space, classify whatever is left over.

`/*!80000 EXECUTE p */` became an empty string, and an empty statement holds no verb at all, so it trivially qualifies as a read. `SELECT 1; /*M! EXECUTE p */` lost its executable comment, and what was left of that batch was a read. The verb was in the text the whole time. The gate saw a read.

The repair is not to strip more carefully. It is to stop treating those forms as comments in the first place. The stripper now flags the executable form as it encounters it instead of quietly discarding it, and the classifier returns the always-refused class on that flag. In the code that class is `HISTORY_AFFECTING`, the third class from earlier, the write that version control cannot undo at all.

```python
cleaned, executable = strip_sql_comments(sql, report_executable=True)
if executable:
    return HISTORY_AFFECTING
```

That return value is a refusal, not a classification that still runs. The gate never lets that class through, whatever the operator has allowed.

## Blind spot two: the escaped quote

Statement splitting is the other half of the same problem. `split_statements` breaks a batch on `;` outside a quoted value, and it tracked quotes without honoring escapes. So `SELECT 'it\'s'; EXECUTE p` closed the literal at the escaped quote. The splitter lost track of where the literal ended, the rest of the batch got absorbed into the first fragment, and the whole thing classified as whatever that first fragment was. The classifier reads the leading keyword of a statement and classifies from that, so a verb sitting further down inside the merged fragment never gets a vote. The fragment still opens with a SELECT, and that leading SELECT is what the gate judged.

Two escape forms matter here, a backslash escape and a doubled quote. Either one ends a literal early if the lexer ignores it.

```python
if quote:
    buf.append(ch)
    if ch == "\\" and i + 1 < n:
        buf.append(sql[i + 1])
        i += 2
        continue
    if ch == quote:
        if i + 1 < n and sql[i + 1] == quote:
            buf.append(sql[i + 1])
            i += 2
            continue
        quote = None
```

The splitter now honors the same backslash and doubled quote escapes the comment scanner already handled. One rule, two places.

## Blind spot three: 1--2 is not a comment

The scanner treated `--` as the start of a line comment. MySQL is stricter than that. `--` opens a comment only when a whitespace or control character follows it, or at end of input.

So `SELECT 1--2; EXECUTE p` is arithmetic followed by a real second statement. A text scanner that strips from `--` to the end of the line throws away `2; EXECUTE p` and leaves `SELECT 1` behind. It deletes the dangerous statement instead of refusing it, which is the worst failure mode available to a gate that is supposed to be conservative.

```python
# MySQL -- comments require following whitespace/control (or EOF).
dash_comment = (ch == "-" and i + 1 < n and sql[i + 1] == "-"
                and (i + 2 == n or ord(sql[i + 2]) <= 32))
```

The `#` comment form did not change. The scanner still treats it as a comment start with no whitespace requirement.

## What the repair bought

Before the fix, the new regression tests failed 82 times on the executable comment cases and 50 times on the lexer cases. Those are failing assertions, not separate test functions. One test function drives a parameterized list of attack strings and asserts the gate decision across every combination of opt-in setting, branch name and database maturity, so a single function can fail dozens of times over. The 105 that the full source suite now passes counts test functions across the six test files, which is why two failure counts can add up past the size of the suite. The installed registration fixtures prove refused calls never reach the inert peer.

The gate is conservative in the way a gate should be. An executing-plan option list is refused whatever it says, because the gate does not interpret dialect specific option values. `EXPLAIN (ANALYZE FALSE) SELECT 1` goes down with `EXPLAIN (ANALYZE TRUE) SELECT 1`, and neither shape changes the answer. Plain `EXPLAIN SELECT * FROM issues` stays a read. Ordinary comments and comment like text inside quoted values stay supported, so `SELECT '/*! EXECUTE p */'` is still just a string.

None of this turns the classifier into a parser. It is a bounded statement classification rule, not a replacement for database permissions, and it does not certify all SQL effects.

The whole gate lives in the [dolt-mcp-vcs-plugin](https://github.com/jeremylongshore/dolt-mcp-vcs-plugin) repository, with the refusal matrix in `tests/test_sql_classifier.py` and the reasoning written up in the README section on indirect SQL execution.

## Use this

- Flag executable comments before you strip them. Detect `/*!`, `/*M!`, and `/*m!` in the scanner, refuse the statement, and keep the original text somewhere a human can read it.
- Split statements with the same escape rules you strip comments with. A backslash escape or a doubled quote inside a literal has to be honored in both passes, or an escaped quote swallows the rest of the batch into one fragment.
- Implement the dialect's comment rule, not a text approximation. In MySQL `--` opens a comment only when whitespace or a control character follows, so `1--2` is arithmetic and the statement behind it has to survive to be classified.

## Related Posts

- [Gate the Statement, Not the Tool Name](https://startaitools.com/posts/gate-the-statement-not-the-tool-name/): why a tool-name allowlist guards nothing when one MCP tool carries every SQL verb
- [Every Verdict Carries the Scope It Actually Ran](https://startaitools.com/posts/a-green-result-only-covers-what-it-ran/): a green suite covers the cases it ran, and the adversarial ones are usually not in that set
- [An Agent Allowlist Is a Comment Until a Gate Checks the Body](https://startaitools.com/posts/agent-allowlist-consistency-gate/): the same principle applied to agent tool grants instead of SQL verbs
