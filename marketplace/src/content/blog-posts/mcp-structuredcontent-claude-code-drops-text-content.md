---
title: "MCP structuredContent: Claude Code Drops Your Text Blocks"
description: "Claude Code, as observed in our check, drops the text blocks of an MCP tool result when structuredContent is set. Put model-facing rules in a note field."
date: "2026-11-05"
tags: ["mcp", "claude-code", "evals", "ai-agents", "typescript"]
featured: false
canonical: "https://startaitools.com/posts/mcp-structuredcontent-claude-code-drops-text-content/"
---
If you build an MCP server, the instructions you write into the text of a tool result may never reach the model.
MCP (Model Context Protocol) lets an AI app such as Claude Code call tools on a server you run. A tool result can carry plain text and a JSON object called `structuredContent`, and the app decides which of the two the model reads.
This post shows how to check what the app actually hands the model, how to put your instructions where they will arrive, and how to stop a test harness from hiding a tool call the app refused.

It is for anyone who ships or tests an MCP server used from more than one AI app.

We found this in a read-only MCP server that answers questions about a team's Discord history.
Its text carried the rules the model is meant to follow, plus a one-line summary and a line saying so when nothing was found. Its JSON carried the messages.
When we checked, Claude Code, Anthropic's coding agent, gave the model the JSON and dropped the text.
Our evals (scripted prompts that grade the model's tool calls and answers) still passed.

## The spec lets a host treat structuredContent and text as equivalent

The MCP specification's Tools section covers structured content. It says:

> For backwards compatibility, a tool that returns structured content SHOULD also return the serialized JSON in a TextContent block.

That lets a host (the AI app that runs the model) treat the two channels as equivalent.
Our server did not send a copy. Its text was different material from its JSON.
It carried framing (the rules, the summary line, the empty-result line) that the JSON did not.
When we checked, Claude Code treated the JSON as the result and dropped the text.

## What Claude Code kept from a structuredContent result

We confirmed this three ways.
The first was Claude Code's minified client code, which we read directly. The branch that matters looks like this:

```javascript
if (e.structuredContent == null) return Re(e.content);
return [...(Re(e.content) ?? []).filter(s => s.type !== "text"), { type: "text", text: _(e.structuredContent) }];
```

When a result has structuredContent, the filter removes every block whose `type` is `"text"`, and the JSON goes in its place.
This is client behaviour we observed. It is not a documented contract.

The second check was the raw `claude -p` stream of an eval run. Every successful tool_result was the JSON.
The third was the deployed server reached through its production connection, which also gave the model JSON only.

## What got lost, and why the evals passed

The server shows each message as a card in apps that draw them, and its rules are named constants in the server code: DATA_RULE, NAME_RULE and CARD_RULE.
Under that filter, the model lost DATA_RULE (13 sites), NAME_RULE, CARD_RULE, every lead line (the one-line summary above a result) such as a count of open messages between you and a named person, and every nothing-found line.

The data survived.
Each card object carried id, where, author, at, text and url.
Citations and the injection cases still passed. They passed on the model's defaults and the eval's own system prompt, not on the server's rules.
A passing eval told us the data arrived. It did not tell us the rules did.

| What the tool result carried | Where it lived | Reached the model (as observed) |
|---|---|---|
| Rules (DATA_RULE, NAME_RULE, CARD_RULE), lead lines, nothing-found lines | Text block | No |
| Messages (id, where, author, at, text, url) | structuredContent JSON | Yes |

## Why the eval showed find_messages twice

We found the lost rules while chasing a repeated call.
The eval runner (the script that sends each case to the model and prints its tool calls) printed my_queue, then find_messages, then find_messages again.
It read as the server making the model search twice, so we started a fix in the server code.

The raw stream showed something else.
The model named find_messages without the MCP server prefix (`mcp__<server>__`).
Claude Code refused it with `No such tool available: find_messages`.
The model then called the prefixed name, `mcp__<server>__find_messages`. There is no server-side retry.

The runner's transcript printer had stripped the prefix, so the refused call and the real one printed the same.
We dropped the server-side change once the stream was clear.

## The fix: a note field inside structuredContent

The fix has two parts.
The first is a `note` field holding the result text with the per-message lines removed, because each of those restates a message object the structured view already carries.
The second changes `reply()`, the one helper that builds a result.
It keeps the text block for hosts that read it, and writes the same framing into structuredContent.
It also takes an error flag, so error results use the same path.

This is the first version of the change (the doc comment is omitted):

```diff
-const reply = (view: View, text: string) => ({ content: [{ type: "text" as const, text }], structuredContent: view });
+export const note = (text: string) => text.split("\n").filter((l) => !l.startsWith("- ")).join("\n");
+const reply = (view: Record<string, unknown>, text: string, isError = false) => ({ content: [{ type: "text" as const, text }], structuredContent: { ...view, note: note(text) }, ...(isError ? { isError: true as const } : {}) });
```

That first `note()` was too blunt, and review caught it before merge.
Stripping every line that starts with "- " assumed the structured view always carries the same data.
It does not. The `start_here` tool lists channel ids as "- " lines, and the view leaves them out unless detail is requested. Glossary terms, trends and FAQ items had the same gap.
Indented message lines in the catch-up tool slipped past the filter too, so those reached the model twice.

The merged `note()` drops only lines in the message shape (where, author, date, quoted text, url) at any indentation, plus an indented continuation under one. Every other list stays.
A further commit before merge let the pattern accept the bracketed flags the timeline tool appends after each url.
Probed on the dev host after the narrowing, the `start_here` note carried 9 channel id lines while the view's channel list was empty, and the catch-up note ran 878 characters against 4,551 of text.
The `reply()` line is the same in both versions.

The sync tool (the owner-only tool that adds a Discord server) had four inline returns that skipped this path.
Two of them carried instructions the model never saw: "Which server? The bot is in: ..." and "Discord asked to wait Ns; call sync again after that."
Both now go through `reply()`. For example:

```typescript
// before
return { content: [{ type: "text" as const, text: `Which server? The bot is in: ${list}.` }], structuredContent: { needs: "guild_id", servers: live } };

// after
return reply({ needs: "guild_id", servers: live }, `Which server? The bot is in: ${list}.`);
```

A unit guard now checks that every structured result takes this path.
The card view ignores `note`, so the cards are unchanged.

## Two obvious alternatives we did not take

The obvious alternative is to drop structuredContent and return text only.
The cards are drawn from the structured data, so that would cost the card in every host that draws one.
The fix keeps the structured result and puts the framing beside the data.

The other obvious alternative is to follow the spec's SHOULD literally and make the text block a serialized copy of the JSON.
That makes the two channels agree, and it deletes the framing from both.
The rules have to live somewhere the model reads, and the structured result is the one place this host passed through.

## Flagging bare-name MCP tool calls in eval output

The runner printed a rejected call the same way it printed an accepted one.
The transcript code moved from the runner to the grader, where it has no side effects and can be unit tested.
A Claude call whose name lacks the server prefix now prints as `<name>?`.
The grader matches on the tool name, so that call no longer counts as the expected tool.
A case cannot pass on a call the host rejected.

Same eval case (`call-prep-nobody`), one run after the change:

```text
PASS  call-prep-nobody  [5s]
      calls: my_queue({"person":"Zelda"}) -> find_messages?({"query":"Zelda"}) -> find_messages({"query":"Zelda"})
```

The case still passes here, because the model's second, prefixed call is the one the grader counts.
Two of three runs showed this miscall. The third went from my_queue straight to find_messages.
Zelda is a seeded fixture name.

## Eval results around the note field fix

The numbers in this section were taken on the first version of `note()` plus the greeting budget, before the narrowing. After the narrowing, the full suite passed 27 of 27 and the greeting case passed 4 of 4, and we did not re-measure token use.

With CARD_RULE reaching the model, the no-card greeting followed it and grew.
It ran 295 to 317 characters, which failed the 300 character cap on the greeting-quiet case (a check that the greeting stays short) in 2 of 4 runs.
On main, the same case passed 4 of 4. We measured by setting the change aside on the same dev host.

The follow-up change gives the no-card branch an explicit budget: "under 200 characters in all, nothing else, since the card would have shown the rest."
The eval cap is unchanged.
Across six runs after that change, the case passed 6 of 6.
Answers ran from 140 to 230 characters, so the top of that range sits above the 200 budget.

In the raw stream, the my_queue, find_messages and start_here results each carried the rule text in `note`.
The full suite passed 27 of 27 in 58 seconds, and the unit suite passed 228 checks, 5 of them new.
Token use stayed flat. The run after the fix used 136 input tokens (345,046 from cache) and 12,159 output tokens.
A baseline run on main used 144 input tokens (326,910 from cache) and 12,664 output tokens.

## A second runner: the same evals through Codex

The same eval suite also runs through OpenAI's Codex CLI, because a server meant for more than one AI app should be measured on more than one.
That run came before the note field, and its first pass found a grader bug. Codex wrote couldn’t with a curly apostrophe, and the "says" patterns only matched the straight one, so two correct answers failed.
Claude never hit it because it types straight quotes.
The grader now normalizes curly quotes in phrase checks.

That run tested the grader. It says nothing about which channel Codex hands the model.
Of 27 cases, 23 ran before an outer time limit cut the rest off, and 17 of those passed.
Of the six failures, three were per-case timeouts, two were the quote bug, and one was a behaviour difference: Codex answers a bare "Hi" without calling `start_here`.

## What is not verified

We did not verify the note field on claude.ai web, claude.ai desktop, or Codex. The environment that ran the checks after the fix was not the one that ran the Codex suite, and it could not reach any of the three. The Codex run above predates the note field.
The text channel is still intact for any host that reads it.
We have no measurement of what those other hosts send the model.

The spec leaves hosts room to pick either channel, so do not assume the text block reaches the model.
Check the raw stream of a run, and read the structured content section of the specification as the contract to design against, not as a promise about any one host: https://modelcontextprotocol.io/specification/2025-06-18/server/tools#structured-content

## Frequently asked questions

### Why does Claude Code drop the text in an MCP tool result?

When a tool result carries structuredContent, Claude Code, as observed at the time of our check, keeps the JSON and removes every text block. The minified client code we read filters out text blocks whenever structuredContent is present. This is observed behaviour, not a documented contract, so check the raw stream of your own runs.

### How do I check what the model actually receives from an MCP tool call?

Run one eval case with the raw stream turned on and check each tool_result. If the tool_result is the JSON alone and a rule you need is not in it, the rule never reached the model. The eval runner's transcript printer is not enough on its own, because it stripped the server prefix and printed a rejected call the same as an accepted one.

### Does the MCP spec require a text block when a tool returns structuredContent?

The MCP Tools section says a tool that returns structured content SHOULD also return the serialized JSON in a TextContent block, for backwards compatibility. That lets a host treat the two channels as equivalent, so the spec leaves hosts room to pick either one. Do not assume the text block reaches the model, and treat the structured content section of the spec as the contract to design against, not a promise about any one host.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Why does Claude Code drop the text in an MCP tool result?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "When a tool result carries structuredContent, Claude Code, as observed at the time of our check, keeps the JSON and removes every text block. The minified client code we read filters out text blocks whenever structuredContent is present. This is observed behaviour, not a documented contract, so check the raw stream of your own runs."
      }
    },
    {
      "@type": "Question",
      "name": "How do I check what the model actually receives from an MCP tool call?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Run one eval case with the raw stream turned on and check each tool_result. If the tool_result is the JSON alone and a rule you need is not in it, the rule never reached the model. The eval runner's transcript printer is not enough on its own, because it stripped the server prefix and printed a rejected call the same as an accepted one."
      }
    },
    {
      "@type": "Question",
      "name": "Does the MCP spec require a text block when a tool returns structuredContent?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The MCP Tools section says a tool that returns structured content SHOULD also return the serialized JSON in a TextContent block, for backwards compatibility. That lets a host treat the two channels as equivalent, so the spec leaves hosts room to pick either one. Do not assume the text block reaches the model, and treat the structured content section of the spec as the contract to design against, not a promise about any one host."
      }
    }
  ]
}
</script>

## Use this

- Run one eval case with the raw stream on and check each tool_result. If the tool_result is the JSON alone and a rule you need is not in it, the rule never reached the model.
- When a result carries structuredContent, put model-facing framing in a field inside it (a note field works), and keep the text block for hosts that read it.
- Have the eval runner print a bare-name or otherwise rejected tool call as a miscall, and make sure a case cannot pass on it.

## Related posts

- [Pin the Eval Dataset With a SHA-256 Digest From the Caller](https://startaitools.com/posts/pin-the-eval-dataset-sha256-digest-from-the-caller/)
- [MCP Server Auth: The API Is the Real Boundary](https://startaitools.com/posts/the-api-is-the-real-boundary/)
- [Green CI Proves Nothing: Why Your Tests Gate Zero Calls](https://startaitools.com/posts/when-green-ci-proves-nothing/)
