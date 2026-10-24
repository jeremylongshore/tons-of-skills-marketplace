# Advanced Eval Workflow

Detailed instructions for empirical skill evaluation, iteration, description optimization,
blind comparison, packaging, and platform-specific adaptations.

Read this reference when using the eval infrastructure (Steps E1-E5), improving skills
through iteration, running automated description optimization, or working on Claude.ai/Cowork.

This reference is opt-in. Execute model/provider evaluations only when requested
and covered by existing authorization for their cases and proof destination.
Keep missing coverage INCOMPLETE and absent runs unverified. Use the available
bounded concurrency; reading this document does not authorize provider calls.

---

## Running and Evaluating Test Cases

This extends Steps 7-8 with concrete tooling for empirical evaluation. The core idea: run
the skill on real prompts, compare against a baseline, grade the results, and show them to
the user in an interactive viewer.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the
workspace, organize by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that,
each test case gets a directory (`eval-0/`, `eval-1/`, etc.). Create directories as you go.

### Step E1: Schedule the authorized with-skill and baseline runs

For each authorized case, compare the same task with and without the skill.
Schedule runs within the available concurrency; preserve the approved matrix.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about>
```

**Baseline run** (same prompt, no skill):

- **Creating a new skill**: no skill at all. Save to `without_skill/outputs/`.
- **Improving an existing skill**: snapshot the old version first (`cp -r`), point baseline
  at the snapshot. Save to `old_skill/outputs/`.

Write an `eval_metadata.json` for each test case:

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### Step E2: While runs are in progress, draft assertions

Don't wait idle. Draft quantitative assertions for each test case and explain them to the
user. Good assertions are objectively verifiable and have descriptive names. Subjective
skills (writing style, design) are better evaluated qualitatively — don't force assertions
onto things that need human judgment.

Update `eval_metadata.json` files and `evals/evals.json` with the assertions. See
[`schemas.md`](schemas.md) for the full schema.

### Step E3: As runs complete, capture timing data

When each subagent task completes, the notification contains `total_tokens` and
`duration_ms`. Save immediately to `timing.json` — this is the only opportunity to
capture this data:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

### Step E4: Grade, aggregate, and launch the viewer

Once all runs are done:

1. **Grade each run** — spawn a grader subagent that reads
   [`../agents/grader.md`](../agents/grader.md) and evaluates each assertion against the outputs.
   Save results to `grading.json` in each run directory. The grading.json expectations array
   must use fields `text`, `passed`, and `evidence` — the viewer depends on these exact field
   names. For programmatically checkable assertions, write and run a script rather than
   eyeballing it.

2. **Aggregate into benchmark**:

   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```

   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for
   each configuration, with mean +/- stddev and the delta. If generating benchmark.json
   manually, see [`schemas.md`](schemas.md) for the exact schema the
   viewer expects.

3. **Analyst pass** — read the benchmark data and surface patterns. See
   [`../agents/analyzer.md`](../agents/analyzer.md) (the "Analyzing Benchmark Results" section) for
   what to look for — non-discriminating assertions, high-variance evals, time/token tradeoffs.

4. **Launch the viewer**:

   ```bash
   nohup python ${CLAUDE_SKILL_DIR}/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```

   For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`.

   **Headless/Cowork:** Use `--static <output_path>` to write standalone HTML instead of
   starting a server.

5. **Tell the user** the viewer is open. They'll see an "Outputs" tab (per-test-case
   feedback) and a "Benchmark" tab (quantitative comparison).

### What the user sees in the viewer

The "Outputs" tab shows one test case at a time:

- **Prompt**: the task that was given
- **Output**: the files the skill produced, rendered inline where possible
- **Previous Output** (iteration 2+): collapsed section showing last iteration's output
- **Formal Grades** (if grading was run): collapsed section showing assertion pass/fail
- **Feedback**: a textbox that auto-saves as they type
- **Previous Feedback** (iteration 2+): their comments from last time

The "Benchmark" tab shows the stats summary: pass rates, timing, and token usage for each
configuration, with per-eval breakdowns and analyst observations.

Navigation is via prev/next buttons or arrow keys. When done, "Submit All Reviews" saves
all feedback to `feedback.json`.

### Step E5: Read the feedback

When the user is done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user thought it was fine. Focus improvements on test cases with
specific complaints. Kill the viewer server when done: `kill $VIEWER_PID 2>/dev/null`.

---

## Improving the Skill

After running test cases and collecting feedback, improve the skill based on what you learned.

### Key principles

1. **Generalize from feedback.** Skills may be invoked millions of times across many prompts.
   Don't overfit to the few test examples — generalize from failures to broader categories of
   user intent. Rather than fiddly overfitty changes or oppressive MUSTs, try branching out
   with different metaphors or patterns. It's cheap to experiment.

2. **Keep the prompt lean.** Remove what isn't pulling its weight. Read transcripts, not just
   outputs — if the skill makes the model waste time on unproductive steps, remove those
   instructions.

3. **Explain the why.** Try to explain *why* things matter rather than just prescribing rules.
   Today's LLMs are smart — they have good theory of mind and when given a good harness can
   go beyond rote instructions. If you find yourself writing ALWAYS or NEVER in all caps,
   reframe and explain the reasoning. That's more humane, powerful, and effective.

4. **Look for repeated work.** If all test runs independently wrote similar helper scripts,
   that's a signal the skill should bundle that script in `scripts/`. Write it once and tell
   the skill to use it.

### The iteration loop

After improving the skill:

1. Apply improvements to the skill
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baselines
3. Launch the reviewer with `--previous-workspace` pointing at the previous iteration
4. Wait for the user to review and tell you they're done
5. Read new feedback, improve again, repeat

Keep going until:

- The user says they're happy
- The feedback is all empty (everything looks good)
- You're not making meaningful progress

---

## Description Optimization (Automated)

The description field is the primary mechanism determining whether Claude invokes a skill.
After creating or improving a skill, offer to optimize the description for better triggering
accuracy.

### Step D1: Generate trigger eval queries

Create 20 eval queries — a mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

Queries must be realistic — concrete, specific, with details like file paths, personal
context, column names. Include casual speech, typos, abbreviations. Focus on edge cases
rather than clear-cut examples.

For **should-trigger** (8-10): different phrasings of the same intent, cases where the user
doesn't name the skill but clearly needs it, uncommon use cases, cases where this skill
competes with another but should win.

For **should-not-trigger** (8-10): near-misses — queries sharing keywords but needing
something different. Adjacent domains, ambiguous phrasing where naive keyword match would
trigger but shouldn't. Don't make negatives obviously irrelevant.

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`
Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin"`

### Step D2: Review with user

Present the eval set using the HTML template:

1. Read [`../assets/eval_review.html`](../assets/eval_review.html)
2. Replace placeholders: `__EVAL_DATA_PLACEHOLDER__` (JSON array, no quotes — it's a JS
   variable assignment), `__SKILL_NAME_PLACEHOLDER__`, `__SKILL_DESCRIPTION_PLACEHOLDER__`
3. Write to `/tmp/eval_review_<skill-name>.html` and open it
4. User edits queries, toggles triggers, clicks "Export Eval Set"
5. Read the exported file from `~/Downloads/eval_set.json` (check for `eval_set (1).json` etc.)

### Step D3: Run the optimization loop

Tell the user this will take some time. Save the eval set to the workspace, then run:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

Use the model ID from your system prompt so the triggering test matches what the user
actually experiences.

This splits 60% train / 40% test, evaluates the current description (3 runs per query for
reliability), proposes improvements based on failures, and iterates up to 5 times. Returns
JSON with `best_description` selected by test score to avoid overfitting.

### How skill triggering works

Skills appear in Claude's `available_skills` list with their name + description. Claude
decides whether to consult a skill based on that description. Important: Claude only consults
skills for tasks it can't easily handle alone — simple one-step queries may not trigger even
if the description matches. Complex, multi-step, or specialized queries reliably trigger when
the description matches.

Eval queries should be substantive enough that Claude would benefit from consulting a skill.

### Step D4: Apply the result

Take `best_description` from the JSON output and update the skill's SKILL.md frontmatter.
Show the user before/after and report the scores.

---

## Advanced: Blind Comparison

For rigorous comparison between two skill versions, use the blind comparison system. Read
[`../agents/comparator.md`](../agents/comparator.md) and [`../agents/analyzer.md`](../agents/analyzer.md) for
details.

The basic idea: give two outputs to an independent agent without telling it which is which,
and let it judge quality. Then analyze why the winner won.

This is optional, requires subagents, and most users won't need it. The human review loop
is usually sufficient.

---

## Packaging

Package a skill into a distributable `.skill` file:

```bash
python -m scripts.package_skill <path/to/skill-folder> [output-directory]
```

This validates the skill first, then creates a zip archive excluding `__pycache__`,
`node_modules`, `evals/`, and `.DS_Store`.

Only package if `present_files` tool is available or the user requests it. After packaging,
direct the user to the resulting `.skill` file path so they can install it.

---

## Platform-Specific Notes

### Claude.ai

The core workflow (draft -> test -> review -> improve) is the same, but without subagents:

- **Test cases**: Run them yourself one at a time. Skip baseline runs.
- **Review**: Present results directly in conversation. Save output files and tell the user
  where they are.
- **Benchmarking**: Skip quantitative benchmarking — it relies on baselines.
- **Description optimization**: Requires `claude` CLI — skip on Claude.ai.
- **Packaging**: `package_skill.py` works anywhere with Python.
- **Updating existing skills**: Preserve the original name. Copy to `/tmp/` before editing
  (installed path may be read-only). If packaging manually, stage in `/tmp/` first.

### Cowork

- You have subagents — the full workflow works, though you may need to run test prompts in
  series if timeouts occur.
- No browser: use `--static <output_path>` for the eval viewer and share the HTML file link.
- Always generate the eval viewer BEFORE evaluating inputs yourself — get results in front
  of the human ASAP.
- Feedback: "Submit All Reviews" downloads `feedback.json` as a file.
- Description optimization (`run_loop.py`) works since it uses `claude -p` via subprocess.
- Save description optimization until the skill is fully finished and the user agrees it's
  in good shape.
