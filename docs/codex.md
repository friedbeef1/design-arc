# Design Arc for Codex — Live

[Home](../README.md) · [Getting started](getting-started.md) · [Using Design Arc](using-design-arc.md) · [Codex](codex.md) · [Claude Code](claude-code.md) · [Google Antigravity](antigravity.md) · [FAQ](faq.md) · [Runtime boundaries](runtime-boundaries.md) · [Advanced controls](advanced-controls.md) · [Evidence and methodology](evidence-and-methodology.md) · [Upgrades and migration](upgrades-and-migration.md) · [Migration history](migration-history.md) · [Trust and sources](trust-limitations-and-sources.md)

Choose the Codex edition when your product work already happens in Codex.

**Release status: Live.** This is the established Design Arc adapter for regular use.

## Install

[Install the Live Codex edition from the OpenAI Plugin Directory](https://chatgpt.com/plugins/plugins_6a82ffefdc88819191f5eaab4eaf116b).

GitHub remains the public source and fallback Codex marketplace. If you need that route, ask Codex:

> Install the Design Arc plugin from https://github.com/friedbeef1/design-arc

Then open the product project and say:

> Use Design Arc to help me improve our onboarding.

That ordinary-language request is the recommended start. If you prefer a shortcut, use `$design-arc`; the paired Claude Code form is `/design-arc:design-arc`.

## What Codex adds

- A pinned project home, created only with your approval, so Design Arc is easy to find later.
- Static screen images and complete journey boards directly in Codex by default.
- An upfront choice between Codex, Stitch, or both, with both recommended for direct comparison.
- Codex-specific preferences and review records under `.codex/`.

## Guided Stitch connection

The Live Codex plugin already includes the Stitch MCP connection definition. You do not need to search for, select, or install a separate Stitch MCP.

When you choose Stitch or both at the upfront visualization decision, Codex verifies the bundled `https://stitch.googleapis.com/mcp` connection with a read-only project-list request. If credentials are missing, Codex prompts you to enter your key securely. To create one, open [Google Stitch](https://stitch.withgoogle.com/), then go to Profile Picture → **Stitch settings** → **API key** → **Create key**.

Never paste a Stitch API key into chat. Enter it only in Codex's secure credential prompt. Design Arc does not read it, put it in project files, save it in preferences, or include it in the plugin.

Codex then verifies the connection again and resumes at the pending visual-workspace choice. A failed connection never blocks the normal Codex board; Design Arc reports the blocker and keeps Stitch optional.

## State

Codex owns `.codex/design-arc.yaml`, its review records, and its graph records. The optional pinned project home remains a Codex-owned return path. This state stays separate from Claude Code state even when both editions are used for the same product.

## Returning later

With your approval, Codex can create one pinned project home for this saved product. It is a launchpad for plain-language starters: each starter opens a clean local task in the same project. Use `$design-arc home` only when you want to inspect, create, recover, or repin that Codex-only return path.

Claude Code has no project home. Its separate, optional return aid is an approved `CLAUDE.md` reminder; see [Design Arc for Claude Code](claude-code.md).

## Commands when you want them

Every shared setting has matching Codex and Claude Code syntax in [Advanced controls](advanced-controls.md). For example, use `$design-arc evidence guidelines` in Codex or `/design-arc:design-arc evidence guidelines` in Claude Code. These shortcuts are optional: “Use official guidelines only” means the same thing for the current review.

## Upgrade

Ask Codex to upgrade Design Arc safely through its configured marketplace. Before the change, verify the installed version, requested version, source, and route; afterward, verify the installed result.

The upgrade preserves `.codex/design-arc.yaml`, the optional pinned project home, review records, graph records, product files, and active tasks byte-for-byte. It does not rerun setup, recreate homes, or change an active review. After verifying the installed version and preservation result, start the next review in a clean Codex task.

Codex does not synchronize, merge, import, or mutate Claude Code state.

## What stays the same

The objective confirmation, credible-source grounding, evidence modes, approval gates, complete-state validation, graph-assisted reasoning, optional Stitch workflow, three-round correction loop, and implementation boundaries are the same Design Arc methodology used by the Claude Code edition.

The pinned project home is a return shortcut, not a second product or a separate copy of your application. See [Projects and AI coding platforms](faq.md#projects-and-ai-coding-platforms) in the FAQ for the plain-language explanation.

Commands are optional and live in [Advanced controls](advanced-controls.md).
