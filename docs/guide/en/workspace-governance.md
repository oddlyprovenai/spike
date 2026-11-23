# Backups, Data Wipe, Command Palette, Task Space, and GitHub Skill Inspector

Language: [Español](../es/workspace-governance.md) | **English** · [Guide Index](README.md)

![Privacy, Backup, and Workspace Governance](../images/privacy-and-spend.png)

## What it does

Groups SPIKE's local-ownership and navigation controls introduced for `v0.1`: SHA-256-verified ZIP backups with dry-run restore previews, typed-confirmation full data deletion, the `Ctrl+K` / `Cmd+K` Command Palette and replayable Guided Tour, six one-click bilingual Sample Projects, the unified **Task Space** timeline for multi-step runs and in-app Dev Sessions, the license-gated GitHub `SKILL.md` archive inspector, and the redacted local error log.

## Step-by-step usage

1. **Navigate with the Command Palette (`Ctrl+K` / `Cmd+K`):** press `Ctrl+K` (`⌘K` on macOS) from anywhere in the app to jump across views, switch specialists, open a project, search conversation history, or launch an in-app Dev Session using arrow keys, `Enter`, and `Esc`. Re-open the first-run **Guided Tour** or inspect all shortcuts at any time in **Settings → Help**.
2. **Explore with Sample Projects:** open **Projects** and import any of the six ready-made EN/ES starter projects (expenses spreadsheet, report brief, mini web page, handbook, visual workflow, or paper-only finance case) in one click without touching external networks.
3. **Inspect multi-step work in Task Space:** click **View task** on any multi-step chat answer or open the side panel of an in-app **Dev Session** (`/api/dev/*`) to see every step's status, every permission decision (`allowed once`, `allowed always`, `denied`, `blocked by settings`), modified files with one-click undo, and downloadable deliverables — reconstructed purely from stored run events even after a server restart.
4. **Install a `SKILL.md` from GitHub safely (`Settings → Skills`):** paste a repository URL to run a read-only preview (`POST /api/skills/import-github/preview`). SPIKE checks that the repository declares a permissive license (`MIT`, `Apache-2.0`, `BSD`, or `ISC`), displays `SKILL.md` and every file with its SHA-256 digest before writing to disk, and keeps newly installed skills **disabled** until you explicitly enable them. No model call can trigger an install.
5. **Back up, preview, restore, or wipe your data (`Settings → Privacy`):**
   - **Export backup (`GET /api/backup/export`):** downloads a `.zip` of settings, chats, Neural Memory, projects, and custom skills with per-file SHA-256 checksums — **never** API keys or connector secrets.
   - **Restore (`POST /api/backup/preview` → `POST /api/backup/restore`):** inspects the archive first and asks before overwriting any existing file (`overwrite=1`).
   - **Delete all data:** requires typing the confirmation word; downloaded `.gguf` models and stored OS-keychain keys are removed **only** if their dedicated checkboxes are ticked, and SPIKE refuses to wipe a directory that is not a dedicated SPIKE data folder.
6. **Copy redacted diagnostics (`Settings → Errors`):** review the local ring buffer of recent internal errors (message payloads, file contents, and API keys are excluded; local paths are shortened) and click **Copy as issue** to copy plain text to your clipboard — nothing is transmitted automatically.

## Real limits

- Backup, restore, full wipe, Dev Sessions, and error-log endpoints accept requests **only from the computer SPIKE runs on** (`403` if called from another origin or host).
- Backup archives intentionally omit OS-keychain API keys and connector secrets; after restoring on a new machine, re-enter external provider keys in **Settings → Providers**.
- Task Space reconstructs saved run events deterministically; how effectively the 4B local model completes multi-step coding sessions on real repositories is **not measured** with real weights yet ([../../STATUS.md](../../STATUS.md)).

## How to verify

- Run the offline test suites covering backup/restore, wipe safety, onboarding/command palette, sample projects, Task Space, GitHub skill import, and redacted error logs:
  `.venv/bin/python -m pytest -q tests/test_backup_g34.py tests/test_wipe_g36.py tests/test_onboarding_g33.py tests/test_samples.py tests/test_dev_api.py tests/test_skill_import_o3.py tests/test_error_log_g43.py`
- Run the frontend unit tests:
  `cd web && npx vitest run src/dataBackup.test.tsx src/taskSpace.test.tsx src/devSessions.test.tsx src/errorLog.test.tsx`
