# Free JT7 Agent Bootstrap (VS Code Extension)

This extension auto-activates Free JT7 instructions in any workspace you open.

## What it does

- Activates on VS Code startup (`onStartupFinished` activation event).
- Creates `AGENTS.md` at workspace root (default).
- Creates `.github/copilot-instructions.md` (optional, enabled by default).
- Creates `.github/free-jt7-trace.md` (persistent plan/task traceability log).
- Creates Free JT7 runtime files:
  - `.github/agents/free-jt7.agent.md`
  - `.github/agents/skill-creator.agent.md`
  - `.github/free-jt7-policy.yaml`
  - `.github/free-jt7-model-routing.json`
  - `.github/skills/.skills_index.json`
  - `.github/skills/free-jt7-core/SKILL.md`
  - `.github/skills/skill-creator/SKILL.md`
- Syncs VS Code settings to the active project path (fixes hardcoded-path issues).
- Adds command: `Free JT7: Provision Agent In Workspace`.
- Adds command: `Free JT7: Start OpenClaw Gateway Now`.
- Can auto-start OpenClaw gateway through `skills_manager.py`.
- If `gateway-start` fails/timeout, it falls back to detached `node openclaw.mjs gateway`.

## Default behavior

By default, existing files are not overwritten.

Config keys:

- `freeJt7Agent.autoProvision` (`true`)
- `freeJt7Agent.overwriteExistingFiles` (`false`)
- `freeJt7Agent.createCopilotInstructions` (`true`)
- `freeJt7Agent.createTraceabilityFile` (`true`)
- `freeJt7Agent.showNotifications` (`true`)
- `freeJt7Agent.agentFileName` (`AGENTS.md`)
- `freeJt7Agent.syncVsCodeSettings` (`true`)
- `freeJt7Agent.settingsTarget` (`workspace`)
- `freeJt7Agent.enableSkillCreatorAgent` (`true`)
- `freeJt7Agent.openClawAutoStart` (`true`)
- `freeJt7Agent.openClawProjectPath` (`""`)
- `freeJt7Agent.openClawStatusCommand` (`python skills_manager.py gateway-status`)
- `freeJt7Agent.openClawStartCommand` (`python skills_manager.py gateway-start`)
- `freeJt7Agent.openClawCommandTimeoutMs` (`120000`)
- `freeJt7Agent.openClawAutoDetectWorkspaceManager` (`true`)

## Package as VSIX

From this folder:

```powershell
cmd /c npm install
cmd /c npm run package
```

This generates a `.vsix` file.

## Install

Use one of these options:

1. VS Code UI:
   - Extensions panel -> `...` menu -> `Install from VSIX...`
2. CLI:

```powershell
code --install-extension free-jt7-agent-0.3.1.vsix
```

## Notes

- Works for any project/folder opened in VS Code.
- If you need to force-refresh files, set `freeJt7Agent.overwriteExistingFiles` to `true` and run the command manually.
