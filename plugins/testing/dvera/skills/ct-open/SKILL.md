---
name: ct-open
description: Launch CT with the current workspace. Use when you need to inspect the project visually in CT IDE during agent work.
---

# /ct-open — Launch CT

**Primary request**: Use when you want to launch CT with the current workspace.

**Entry**: Any time (no state prerequisite)
**Input**: None
**Output**: CT process launched (asynchronous)

## Steps

### Step 1: Resolve bootstrap variables

**`ctHome` resolution order**:
1. If another CT skill in this conversation (e.g., `ct-init-project`, `ct-orchestrator`) has already established `ctHome`, reuse that value.
2. Otherwise check the OS-specific default installation path once:
   - Windows: `C:\Program Files\Suresoft\CT 2026`
   - Linux: `$HOME/Suresoft/CT 2026`
3. Accept the default only when both conditions hold:
   - Windows: `{ctHome}/python/python.exe` exists. Linux: `{ctHome}/python/python3` exists.
   - A `ct_tool.py` candidate is found via `glob({ctHome}/plugins/*/scripts/ct_tool.py)`.
4. If validation fails or the OS is not Windows/Linux, ask the user with the **standard prompt**:

```text
The CT installation could not be verified.
Provide the installation path to continue.

[Installation check]
• Checked CT installation path: {ctHome or "not configured"}
• Requirement: CT 2026.06 or later
• Note: A valid CT license is required to run CT.

[If CT is already installed]
• Please provide the full path to the CT installation folder.
  Example: C:\Program Files\Suresoft\CT 2026

[If CT is not installed]
• Product and installation support: bizcenter@suresofttech.com
```

Environment variables (`CT_HOME`, etc.), the system PATH, and any heuristics beyond the defaults above are all forbidden.

**Once `ctHome` is confirmed, derive `ctPython` and `ctTool`** — used by the ct_tool.py calls in later steps.

- `ctPython`: Windows `{ctHome}/python/python.exe`, Linux `{ctHome}/python/python3`
- `ctTool`: first match of `glob({ctHome}/plugins/*/scripts/ct_tool.py)`

### Step 2: Resolve the workspace to launch with

Decide the path to pass to CT's `-data`.

1. Read `currentWorkspace` (the CT service's active Eclipse workspace).
   ```bash
   {ctPython} {ctTool} call ct_get_env --json "{}"
   ```

2. **If `currentWorkspace` is non-empty and exists on disk, take it as `{workspace}` directly and proceed to Step 3 without asking.** The user is already working in this workspace, so re-confirming is unnecessary.

3. Only when `currentWorkspace` is empty or does not exist on disk, ask the user.
   - Read the CT IDE workspace history (best-effort).
     ```bash
     {ctPython} {ctTool} call ct_list_recent_workspaces --json "{}"
     ```
   - List `exists=true` entries deduped by path, and always include "enter a new path".

     > "Pick a workspace to launch CT with, or enter a new path.
     > 1. {path}  ← most recently used in CT IDE
     > 2. {path}
     > ...
     > Or enter a new workspace path."

   - If `ct_list_recent_workspaces` fails or returns no usable entries, ask for the path directly.

The chosen or auto-adopted path becomes `{workspace}` for Step 4. Do not call `set-workspace` here — opening the GUI does not require changing the CT service's active workspace.

### Step 3: Shut down the CT Bridge

The CT GUI holds the workspace lock (`.metadata/.lock`), so always shut down the Bridge daemon before Step 4.

```bash
{ctPython} {ctTool} shutdown
```

**Interpreting the response**:
- Bridge was running: `{"success": true, ...}`
- Bridge was not running: exit code 1 with a connection-failure message such as `{"success": false, "error": "..."}` (e.g., `cannot connect to server`, `Connection refused`). **This is expected — proceed to Step 4** — it just means there was no Bridge to shut down. Do not surface it to the user as an error.

The Bridge will auto-restart on the next ct_tool.py call when needed.

### Step 4: Launch CT

Detect the OS and launch CT **in the background** with `{workspace}` from Step 2. CT is a GUI process that lives until the user closes the window, so a foreground call will time out the tool.

**Windows:**
```powershell
Start-Process -FilePath "{ctHome}\CodeScroll.exe" -ArgumentList @('-data', '{workspace}')
```

**Linux:** (`Run_CodeScroll.sh` runs `./CodeScroll` via a relative path, so it must be invoked from `{ctHome}`)
```bash
(cd "{ctHome}" && nohup ./Run_CodeScroll.sh -data "{workspace}" >/dev/null 2>&1 &)
```

### Step 5: Report result

```text
CT has been launched.
Workspace: {workspace}

Once CT is fully open, select the project from the Project Explorer.
```

## Guardrails

- **Do**:
  - When `currentWorkspace` exists on disk, launch directly with it without asking. Otherwise, when listing workspace candidates, always include an "enter a new path" option.
  - Detect the OS and use `CodeScroll.exe` on Windows and `Run_CodeScroll.sh` on Linux.
  - Report the result immediately after launching and continue with other work.
- **Don't**:
  - Do not run CT in the foreground. Use the background command forms above (`Start-Process` / `nohup ... &`) as-is and move on to Step 5 immediately.
  - Do not pull `ctHome` from environment variables or the system PATH, or guess locations beyond the defaults above.
- Do not call `set-workspace` here — opening the GUI does not need to change the CT service's active workspace.
- **Stop and Ask**:
  - If `ctHome` cannot be resolved from the default and the user has not provided one, ask using the standard prompt.
  - If the executable is not found at `{ctHome}`, ask the user to verify CT installation.

## CT Functions

- `ct_get_env()` — Used here to read `currentWorkspace`.
- `ct_list_recent_workspaces()` — Best-effort source of CT IDE workspace history (`path`, `exists`, `isLastUsed`). On failure the skill falls back to a plain prompt.
