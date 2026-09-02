---
name: design-arc
description: Use when a mobile or web product journey feels confusing, incomplete, inconsistent, or subject to taste-based redesign debate, or when a team needs evidence-backed directions and complete material states before implementation.
---

## Codex-only external connection onboarding

Run this connection check when the user selects Stitch or Both at the upfront renderer choice. It is onboarding for an optional external visualizer, not another approval gate.

Support the natural request: `Connect Stitch for Design Arc.` If no review is paused, run the same verification and finish by reporting whether Stitch is ready.

### Stitch

1. A GitHub-marketplace installation includes the Stitch MCP connection definition for `https://stitch.googleapis.com/mcp`; an OpenAI Plugin Directory installation currently omits `mcpServers` and must not be assumed to include it. Inspect the Stitch tools actually available in the current Codex task; never infer a working connection from the bundled definition or server name alone.
2. Verify a plausible Stitch connection with a read-only `list_projects` call or its exact equivalent. A successful call proves the connection even when it returns zero accessible projects; a failed or unauthorized call does not. Report only the count and the minimum project identifiers needed for verification, without exposing unrelated project details.
3. If no verified connection exists, explain exactly: Stitch provides polished, editable mockups on a visual canvas for continued exploration and refinement. Offer `Connect Stitch now — recommended`.
4. If the connection definition is absent, offer to configure the public endpoint and secure header reference in the user's Codex MCP configuration before asking for the key-entry step. Obtain approval before changing the Codex profile. Configure `https://stitch.googleapis.com/mcp` and map `X-Goog-Api-Key` to the secure `STITCH_API_KEY` environment reference; never place the key itself in configuration. The user must not need to search for an MCP.
5. Tell the user exactly where to create the key: open [Google Stitch](https://stitch.withgoogle.com/), select the Profile Picture, then **Stitch settings** → **API key** → **Create key**. The bundled connection sends the secure `STITCH_API_KEY` environment reference as the `X-Goog-Api-Key` header; it never contains a literal credential.
6. Never ask the user to paste a Google API key into chat, and never read, display, log, write, commit, or store it in Design Arc state or project files. Ask the user only to complete the unavoidable key entry through Codex's secure credential interface.
7. After setup, rediscover the Stitch tools and repeat the read-only project-list verification. After successful verification, resume at the pending renderer choice without repeating setup, Objective Confirmation, journey inspection, evidence gathering, or direction approval.
8. If verification still fails, report the exact connection or authorization blocker and continue to offer the Codex visualization route; Stitch remains optional.
9. Do not start a selected Stitch renderer until verification succeeds or the user explicitly chooses the Codex-only fallback.
10. Do not claim that a paid Stitch subscription is required unless current official Google documentation establishes it.

Record only the non-secret, review-scoped verification outcome and connection route. Do not add a Design Arc preference field for credentials or connection state. The GitHub package bundles only the remote connection definition; it does not bundle or republish Google's server code.

### Mobbin

When Guidelines + Benchmarks is selected without verified Mobbin access, explain exactly: Mobbin lets Design Arc inspect complete real-product journeys—not merely isolated screenshots. Present the three connection choices defined by the shared workflow, with connection recommended first.

Use [Mobbin account creation](https://mobbin.com/signup) and [Mobbin plans](https://mobbin.com/pricing) so the user never has to search for the correct pages. Recommend Pro for an individual because it includes the complete library and browsing flows; explain that Team is for multiple collaborators and includes Pro capabilities. Treat prices, availability, and quotas as changeable external information and never hard-code a price into the workflow contract.

Never ask for or store Mobbin credentials. Use only separately authorized browser access; do not imply an official Mobbin MCP integration. Verify access by opening and inspecting a relevant complete journey; a homepage, account page, library listing, metadata, popularity, or one screenshot is insufficient. After successful verification, resume the paused review without repeating completed setup, objective, or approval work. If connection is declined or verification fails, offer the one-run Guidelines only path without rewriting saved preferences or making a benchmark-evidence claim.

Mobbin supplies product precedent, never platform compliance; Stitch supplies visualization, never evidence or correctness.
