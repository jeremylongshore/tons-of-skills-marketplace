# Learning Curriculum

Progressive lesson plans for beginner, intermediate, and advanced users. Each lesson follows the **do-then-explain** methodology: run a real command, see the result, THEN get the explanation.

## Teaching Philosophy

1. **Hands-on first.** Every lesson uses real commands on real repos. No slides, no abstract theory.
2. **Do then explain.** Run the command, see the result, then understand what happened.
3. **Check work.** After each step, verify the user's understanding before moving on.
4. **Build on success.** Each lesson builds on skills from previous lessons.
5. **Real-world context.** Use the user's actual project when possible, not toy examples.

---

## Beginner Curriculum

### Lesson 1: GitHub 101 — Your First Commit

**Trigger:** "teach me github", "learn github", "getting started with github"

**Prerequisites:** GitHub account, `gh` CLI installed, authenticated (Setup mode handles this)

**Steps:**

1. **Create a practice repo** (or use their current project)

   ```bash
   gh repo create my-first-repo --public --clone
   cd my-first-repo
   ```

   *After:* "You just created a project on GitHub and downloaded it to your computer. It's like creating a new folder in Google Drive."

2. **Create a file**

   ```bash
   echo "# My First Project" > README.md
   ```

   *After:* "You made a file. Git noticed — let's see what it thinks."

3. **Check status**

   ```bash
   git status
   ```

   *After:* "Git sees a new file it's not tracking yet. It's highlighted in red because it hasn't been saved to git's memory."

4. **Stage the file**

   ```bash
   git add README.md
   ```

   *After:* "You moved the file to the 'staging area' — like putting a letter in an envelope before mailing it. Let's check status again."

5. **Check status again**

   ```bash
   git status
   ```

   *After:* "Now it's green! That means it's ready to be committed (saved to history)."

6. **Commit**

   ```bash
   git commit -m "Add README with project title"
   ```

   *After:* "You just created a save point! This exact version of your project is now recorded forever. The message describes what you did."

7. **Push to GitHub**

   ```bash
   git push -u origin main
   ```

   *After:* "Your save point is now on GitHub too! If your computer exploded right now, your code would be safe. Let's see it online."

8. **View on GitHub**

   ```bash
   gh repo view --web
   ```

   *After:* "That's your project on GitHub! Anyone with the link can see it."

**Check understanding:** Ask the user to make another change, stage it, commit it, and push it — with less guidance this time.

---

### Lesson 2: Branching Basics

**Trigger:** "what are branches", "teach me branches", "how do branches work"

**Prerequisites:** Completed Lesson 1 or equivalent knowledge

**Steps:**

1. **See your current branch**

   ```bash
   git branch
   ```

   *After:* "You're on 'main' — that's the official version of your project."

2. **Create a new branch**

   ```bash
   git switch -c my-experiment
   ```

   *After:* "You just created a copy of your project called 'my-experiment.' Changes you make here won't affect the main version."

3. **Make a change on the branch**
   - Edit a file (guide the user through adding a line to README.md)

4. **Commit the change**

   ```bash
   git add README.md
   git commit -m "Add description to README"
   ```

5. **Switch back to main**

   ```bash
   git switch main
   ```

   *After:* "Look at your README — the change is gone! It's safely stored on the 'my-experiment' branch."

6. **Switch back to the branch**

   ```bash
   git switch my-experiment
   ```

   *After:* "And it's back! Branches let you work on different things without them interfering with each other."

**Check understanding:** "What would happen if you created another branch from main right now? Would it have the experiment change?"

---

### Lesson 3: Your First Pull Request

**Trigger:** "teach me PRs", "what's a pull request", "how do pull requests work"

**Prerequisites:** Completed Lesson 2 or has a branch with changes

**Steps:**

1. **Push the branch**

   ```bash
   git push -u origin my-experiment
   ```

2. **Create a PR**

   ```bash
   gh pr create --title "Add description to README" --body "This adds a short description explaining what the project does."
   ```

   *After:* "You just asked to merge your experiment into the main version. In a team, someone would review your changes before approving."

3. **View the PR**

   ```bash
   gh pr view --web
   ```

   *After:* "This is what your teammates would see. The green lines are things you added, red lines are things you removed."

4. **Merge the PR**

   ```bash
   gh pr merge --merge
   ```

   *After:* "Your experiment is now part of the main project! This is the normal workflow: branch → change → PR → merge."

5. **Clean up**

   ```bash
   git switch main
   git pull
   git branch -d my-experiment        # Delete local branch
   git push origin --delete my-experiment  # Delete remote branch
   ```

---

**Note on intermediate and advanced lessons:** Lessons 4-9 are structured as outlines with concepts and exercise steps. The AI generates the full step-by-step detail at runtime, adapting to the user's level and project context. This is intentional — unlike beginner lessons (which are fully scripted), higher-level lessons require more contextual flexibility.

## Intermediate Curriculum

### Lesson 4: Branch Workflows

**Trigger:** "teach me branching strategies", "branch workflow", "how should I name branches"

**Concepts covered:**

- Feature branch workflow (one branch per feature/fix)
- Branch naming conventions: `feature/`, `fix/`, `chore/`, `docs/`
- When to branch vs. commit directly (spoiler: always branch in teams)
- Keeping branches up to date with main

**Hands-on exercise:**

1. Create a feature branch with proper naming
2. Make a series of small, focused commits
3. Pull latest main and merge/rebase onto your branch
4. Create a PR with a descriptive title and body

---

### Lesson 5: PR Review Flow

**Trigger:** "teach me code review", "how do I review PRs", "PR review process"

**Concepts covered:**

- How to review someone else's code
- Leaving inline comments
- Approving vs. requesting changes
- Review etiquette (be constructive, explain the why)

**Hands-on exercise:**

1. Find an open PR (or create a practice one)
2. Read through the diff
3. Leave at least one comment using `gh`
4. Approve or request changes

---

### Lesson 6: Team Git

**Trigger:** "how do I collaborate", "team git", "working with others"

**Concepts covered:**

- Forking vs. branching (when to use which)
- Keeping a fork in sync with upstream
- Co-authoring commits
- Handling review feedback and pushing updates to a PR

**Hands-on exercise:**

1. Fork a public repo
2. Make a change and create a PR to the original
3. Sync fork with upstream changes

---

## Advanced Curriculum

### Lesson 7: Rebase vs. Merge

**Trigger:** "teach me rebase", "rebase vs merge", "clean git history"

**Concepts covered:**

- When to rebase vs. merge (and why it matters)
- Interactive rebase (`git rebase -i`) for squashing and reordering
- The golden rule: never rebase public history
- `--force-with-lease` vs `--force`

**Hands-on exercise:**

1. Create a branch with several small commits
2. Interactive rebase to squash fixup commits
3. Rebase onto updated main
4. Push with `--force-with-lease` (on a personal branch only)

---

### Lesson 8: GitHub Actions Basics

**Trigger:** "teach me CI/CD", "github actions", "automated testing"

**Concepts covered:**

- What CI/CD is and why it matters
- GitHub Actions workflow syntax (YAML)
- Common workflow triggers (push, PR, schedule)
- Status checks on PRs

**Starter workflow example:**

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm install
      - run: npm test
```

**Hands-on exercise:**

1. Create `.github/workflows/ci.yml` with the starter workflow above
2. Push and watch it run via `gh run list` and `gh run watch`
3. See how it appears on a PR as a status check

---

### Lesson 9: Review Ecosystem

**Trigger:** "code review apps", "how do code review apps work", "automated review"

**Reference:** See [`github-review-apps.md`](github-review-apps.md) for full details.

**Concepts covered:**

- The ecosystem of automated review tools
- How they integrate with GitHub's PR workflow
- Setting up CodeRabbit or similar tool on a repo
- Reading and acting on automated review comments

**Hands-on exercise:**

1. Install a review app (CodeRabbit recommended) on a test repo
2. Create a PR and observe the automated review
3. Compare automated feedback with what a human reviewer would say

---

## Lesson Delivery Guidelines

### Before Each Lesson

- Confirm the user's environment is ready (correct directory, authenticated, etc.)
- If using their real project, create a safe branch for practice
- Set expectations: "This will take about 10 minutes and we'll do everything hands-on"

### During Each Lesson

- Run commands one at a time, explain after each result
- If the user makes a mistake, fix it together — mistakes are learning moments
- If the user seems to already know something, skip ahead
- If the user seems confused, slow down and use simpler language

### After Each Lesson

- Summarize what they learned (2-3 bullet points)
- Give them a small challenge to do on their own
- Suggest the next lesson based on their interests
