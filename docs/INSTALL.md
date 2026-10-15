# Installing Abacus

## Prerequisites

| Tool | Why | Install |
|---|---|---|
| Python 3.9+ | every Abacus CLI and hook (stdlib only, no pip installs) | macOS: `xcode-select --install`; Linux: your package manager (`python3`) |
| git | gates, verification, publishing | macOS: `xcode-select --install`; Linux: your package manager (`git`) |
| Claude Code with Agent View | background sessions (`claude --bg`, `claude agents`), Dynamic Workflows, SendMessage | `npm i -g @anthropic-ai/claude-code`, then `claude update` |
| Beads (`bd`) | the per-repository system of record for agent work | `brew install beads`, or `npm install -g @beads/bd` |

`abacus doctor` checks all of these, and for anything missing names the install command for your system (it finds
apt, dnf, yum, pacman, zypper or apk on Linux).

**Platforms.** Tested on macOS. Linux should work but is untested: Abacus itself is standard-library Python, git and
Claude Code, so the open question is whether Claude Code's background sessions and Agent View behave the same there.
Windows is untested; use WSL rather than native Windows (Abacus relies on shell scripts and git hooks). The
JavaScript workflow tests run only on macOS (they use its built-in JavaScript engine) and are skipped elsewhere.

**One-time operator steps (Claude Code safety prompts that only a person should accept):**
- **Workspace trust.** A background session can start only in a folder you have trusted. That covers every worker
  repository plus each agent's folder under `~/.abacus/agents/` (concierge, orchestrator, planner). `abacus doctor` lists the ones
  still untrusted, and `abacus trust` opens each in turn: accept the prompt, then `/exit`. Until then,
  `abacus-session start` refuses with `TRUST`. Trust is per path, so it survives rebuilding a demo in the same place.
- **Bypass disclaimer (only if you opt a repo into `bypassPermissions`).** Abacus defaults to `auto` mode. If you later
  promote a repository to bypass (after its guards are ADOPTED and the refusal log looks healthy), run
  `claude --dangerously-skip-permissions` once and accept. Until then the launcher refuses with `OPERATOR`.

## Install

Clone the four repositories side by side, e.g. under `~/Source/repos`:

```sh
cd ~/Source/repos
for r in abacus abacus-standards abacus-infra abacus-agents; do git clone https://github.com/dasien/$r.git; done
```

Then:

```sh
cd ~/Source/repos/abacus
./install.sh --workspace ~/Source/repos     # add --yes to accept every offer
# open a new terminal if the installer added the PATH line, then:
abacus doctor
```

The installer is guided. It checks prerequisites and offers `brew install beads` if Beads is missing. It offers to
append the `PATH` line to your shell's rc file and to enable the status line. A program can't change the PATH of
the shell that started it, so it also links `abacus` into a folder that's already on your PATH (Homebrew's `bin`,
`/usr/local/bin`, `~/.local/bin` or `~/bin`, never replacing anything already called `abacus`), which means `abacus`
works in the same terminal. It finishes by running `abacus doctor` and listing whatever is left, usually just
trusting folders.

Putting `~/.abacus/bin` on your `PATH` is **required**. Your own sessions in adopted repos call `abacus-board`,
`abacus-finalize` and the other CLIs by name. Sessions started with `abacus-session` get it on their `PATH`
automatically, along with the shared-memory server, which is passed explicitly at launch. Claude Code hooks,
`.mcp.json` entries and the git pre-push hook use full paths (`${HOME}/.abacus/bin/...`), so they work either way.

`--workspace` is a directory holding your repositories. It is the **repo-fence boundary**: a worker in one
repository may not write into any other repository under it. If your code lives in several places, repeat it
(`--workspace ~/work --workspace ~/oss`). Demos go in `abacus-sandboxes/` beside the first one. Every repository registered in the fleet
(`~/.abacus/fleet.json`) is fenced too, wherever it lives, so adopting a repository outside the roots still
protects it.

### What install does
1. Checks prerequisites.
2. **Publishes** each repository's committed `HEAD` (this one included) into `~/.abacus/lib/<repo>` and links its
   CLIs, `abacus` among them, into `~/.abacus/bin`. Sessions always run a published snapshot, never your working tree, so a half-edited
   guard can't change a running fleet. Use `--dev` to link working trees while you hack on Abacus itself.
3. Writes `~/.abacus/config.json` (workspace roots, component paths). A reinstall keeps the workspace roots
   unless you pass `--workspace` again, in which case the roots you name replace them, so name them all.
4. Creates `~/.abacus/state/logbook.db` and `~/.abacus/state/memory.db`.
5. Writes `~/.abacus/fleet.json` (the worker registry) if it is absent.
6. Deploys the agents (concierge, planner, orchestrator) into `~/.abacus/agents/` with `abacus-deploy`, and adds any
   new agent to an existing fleet.

### Versions
The four repositories share one version, in `abacus/VERSION`, and each release is tagged `v<version>` in all four.
`abacus --version` prints it along with the commit installed from each repository:
```
abacus 0.7.1
  abacus               9ec03904f08c
  abacus-infra         d345bab49107
  abacus-standards     76373b920a26
  abacus-agents        871ef16b006e
```
Abacus is pre-1.0: the protocol, logbook schema and CLI can still change between minor versions.

**How the version moves.** Every change to any of the four repositories bumps `abacus/VERSION` in the same batch of
commits, and adds a line to [CHANGELOG.md](../CHANGELOG.md):
- **bug fix** → patch: `0.1.0` → `0.1.1`
- **feature added or changed** → minor, and the patch resets: `0.1.1` → `0.2.0`. A batch with both counts as a
  feature.
- **major** (`1.0.0` and later): never bumped as part of a change. The operator decides it explicitly.

Docs-only and test-only changes don't bump the version.

### Status line (optional)
`abacus statusline enable` adds Abacus's state (`abacus · 1 needs you`, `abacus · 1 in flight`) to the status line
of every Claude Code session by editing `~/.claude/settings.json`. It reads only local files, so it is cheap to run
on every redraw.

**If you already have a status line**, `enable` changes nothing and asks you to choose:
- `--wrap` (recommended) keeps yours. Abacus runs your command with the same input, prints its output unchanged,
  and appends `  |  abacus · …` to its last line. Your `padding` and `refreshInterval` are kept. If your command
  fails or takes over 10 seconds, the Abacus part still shows; if Abacus has nothing to say, yours shows alone.
- `--replace` shows only Abacus's.
- Or do it yourself: add `$(~/.abacus/bin/abacus-status --line)` to your own script.

Either flag saves your original, and `abacus statusline disable` puts it back exactly. If you later change your own
status-line command, run `disable`, make the change, then `enable --wrap` again. The installer offers `--wrap`
when it finds a status line of yours.

### Layout of `~/.abacus`
```
bin/            CLI links (on your PATH); abacus-authorize is for you, never for agents
lib/            published component snapshots
config.json     workspace roots, sandbox folder, component paths, where each demo lives
fleet.json      worker registry you edit (source); deployed copy lives in agents/
agents/         deployed roles: concierge/, orchestrator/, planner/, hooks/, fleet.json, .deployed manifest
state/          logbook.db, memory.db, refusals.jsonl, redactions.jsonl (counts only), authorizations/
                (one-time operator grants), locks/, harvest/
```

## Upgrading
`git pull` each component, then re-run `./install.sh` (it keeps your workspace roots). It re-publishes, redeploys, and names any
live role sessions that need a restart. To roll new conventions into an adopted repository, run `abacus-adopt` there,
review the diff, run `abacus-doctor` and commit.

## Uninstalling
Stop sessions (`abacus demo stop`, or `abacus-session stop <name>`), then `rm -rf ~/.abacus`, and remove the
`abacus` link the installer made (`abacus_link` in `~/.abacus/config.json` says where, e.g.
`/opt/homebrew/bin/abacus`). Adopted repositories
keep what `abacus-adopt` wrote:
- `.claude/` (hooks, workflows, skills, settings) and `.abacus/`
- `.githooks/` (run `git config --unset core.hooksPath`)
- the `abacus-memory` entry in `.mcp.json`
- the Abacus block in `CLAUDE.md`
- two `.gitignore` lines
- `docs/retros/` and `docs/adr/`

Remove those if you want them gone.

## Troubleshooting
- **`REFUSED TRUST`**: Claude Code hasn't trusted that folder. Run `abacus trust` (or `claude` there once) and accept.
- **`REFUSED AUTHORITY` or `OPERATOR`**: a worker's `permission_mode` is `bypassPermissions`. Either the repository
  hasn't earned it (`abacus-doctor --check guards`), or you haven't accepted Claude Code's bypass disclaimer. The
  default, `auto`, needs neither. Edit `~/.abacus/fleet.json`, then run `abacus-deploy`: sessions read the deployed
  copy.
- **`command not found: abacus-board`** (or another `abacus-*`) in your own session: `~/.abacus/bin` isn't on your `PATH`.
- **A guard refused something reasonable**: every refusal is logged in `~/.abacus/state/refusals.jsonl`. Classify it as
  fair, false positive or unclear, and file a bead against abacus-standards for false positives.
- **Exit 75 from a push**: heavy-lock contention, not a failing gate. Retry.
