---
name: design-arc
description: Use when a mobile or web product journey feels confusing, incomplete, inconsistent, or subject to taste-based redesign debate, or when a team needs evidence-backed directions and complete material states before implementation.
argument-hint: "[setup|mode|graph] [options]"
user-invocable: true
---

Never tell a Claude Code user to pass work to Codex unless the user explicitly requests a cross-platform handoff.

## Claude Code entry points

Use `/design-arc:design-arc setup` to resolve Design Arc setup,
`/design-arc:design-arc mode` to report or change approval mode, and
`/design-arc:design-arc graph` to report or manage graph assistance. The
same workflow applies when a natural-language request explicitly asks to use
Design Arc or describes a journey review; do not require slash-command syntax.

External tools and services remain separately authorized. This plugin bundles
no MCP server, agent, or hook and does not imply connectivity to a benchmark,
visualization, or other external service.

Resolve the Claude Code profile root before any graph-global read or write: use the non-empty `CLAUDE_CONFIG_DIR` value when present, otherwise use `~/.claude`; canonicalize the chosen root and never treat an empty variable as `/`.
Store laptop-global graph safety only at `<resolved Claude Code profile root>/design-arc-global.yaml`; never read or write `/design-arc-global.yaml`.

For Claude Code graph records, define `project_id` as `claude-code:` plus the lowercase SHA-256 hex digest of the UTF-8 canonical project root (the Git top level when available, otherwise the session working directory); recompute it before validation and never store the raw local path in the graph.

## Claude Code project setup and re-entry

For Claude Code, `/design-arc:design-arc` replaces the `$design-arc` examples
in the canonical methodology. Do not run Codex plugin commands, create a Codex
home, or write Claude state under `.codex`; those are Codex-adapter operations.

On new Claude setup, propose every missing preference and obtain explicit confirmation before creating `.claude/design-arc.yaml`.

When `.claude/design-arc.yaml` already exists, treat it as the Claude saved preference, do not offer Codex import, and never overwrite it from `.codex/design-arc.yaml`.

Only when the Claude preference is absent, inspect `.codex/design-arc.yaml`
read-only if it exists. The portable fields are `evidence_mode`,
`benchmark_provider` when valid for Guidelines + Benchmarks, `approval_mode`, and
`graph_assistance`; validate the complete portable mapping before proposing an
import. Codex-only home metadata and all review state are not portable. Show
the proposed values, identify ignored Codex-only fields, and ask for explicit
import approval.

Only after explicit import approval, copy the validated portable values into a new Claude preference file; do not move or rename the Codex file.
Treat the Codex preference file and every Codex active-review, review, graph, and home record as read-only; verify the imported source remains byte-for-byte unchanged.
If the user declines import, leave all Codex state untouched and continue with a fresh Claude setup.
If the Codex file is malformed or any portable value is invalid, import nothing, report the invalid fields without exposing unrelated contents, and offer fresh Claude setup.

After preference confirmation, separately offer this optional project reminder
for `CLAUDE.md` and show the exact proposed block:

```markdown
<!-- design-arc:reminder:start -->
When a UI journey request matches Design Arc, suggest `/design-arc:design-arc` and wait for explicit approval unless the user invoked Design Arc directly. Never claim Design Arc ran unless the skill loaded.
<!-- design-arc:reminder:end -->
```

Writing or creating `CLAUDE.md` requires explicit approval for that exact
reminder action; preference or import approval is not reminder permission.
Preserve every byte outside that exact marked block, including unrelated instructions, spacing, and final-newline state.
Before writing, detect the exact markers; add the block only when absent, keep exactly one block when present, and never append a duplicate.
If permission is denied, do not create or modify `CLAUDE.md`; complete confirmed preference setup without the reminder.
If safe automatic insertion is unavailable or the write fails, leave `CLAUDE.md` unchanged, say that the reminder was not installed, and return the exact block plus manual insertion steps.

### Safe Claude Code plugin upgrade

An upgrade or downgrade changes the Claude Code plugin installation, not any
participating product and not the Codex adapter. Before changing the installed
plugin, report the installed and requested versions, marketplace source, and
exact route; require confirmation unless the current request already authorizes
that exact change. Re-read installed state afterward instead of trusting command
success, and use only a supported Claude Code plugin route.

Do not run project setup, edit `.claude/design-arc.yaml` or `CLAUDE.md`, touch
product files, or continue an active review during an adapter change. Compare
the participating Claude preferences, reminder blocks, active-review records,
review directories, and graphs byte-for-byte before and after. If any changed,
stop, report the exact affected project, and restore the prior plugin when the
adapter route changed it; never rewrite project state automatically.

An already-open Claude Code session retains its pinned runtime and workflow
version. Do not force-close, convert, merge, or resume it as part of an upgrade
or downgrade; start a new clean session to load the changed adapter version.
