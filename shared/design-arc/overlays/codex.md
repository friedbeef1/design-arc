---
name: design-arc
description: Use when a mobile or web product journey feels confusing, incomplete, inconsistent, or subject to taste-based redesign debate, or when a team needs evidence-backed directions and complete material states before implementation.
---

## Codex-only Stitch connection onboarding

Run this connection check when the user selects Stitch or Both at the upfront renderer choice. It is onboarding for an optional external visualizer, not another approval gate.

1. The Live Codex plugin includes the Stitch MCP connection definition for `https://stitch.googleapis.com/mcp`; the user does not need to find or install a separate Stitch MCP. Inspect the Stitch tools actually available in the current Codex task; never infer a working connection from the bundled definition or server name alone.
2. Verify a plausible Stitch connection with a read-only `list_projects` call or its exact equivalent. A successful call proves the connection even when it returns zero accessible projects; a failed or unauthorized call does not. Report only the count and the minimum project identifiers needed for verification, without exposing unrelated project details.
3. If no verified connection exists, explain the benefit in this one sentence: Stitch provides an editable canvas for visual alternatives and sustained refinement. Then ask the user to enter their Stitch API key in Codex's secure credential prompt; do not ask them to find or install an MCP.
4. Tell the user exactly where to create the key: open [Google Stitch](https://stitch.withgoogle.com/), select the Profile Picture, then **Stitch settings** → **API key** → **Create key**. The bundled connection sends the secure `STITCH_API_KEY` environment reference as the `X-Goog-Api-Key` header; it never contains a literal credential.
5. Never ask the user to paste a Google API key into chat, and never read, display, log, write, commit, or store it in Design Arc state or project files. Ask the user only to complete the unavoidable key entry through Codex's secure credential interface.
6. After setup, rediscover the Stitch tools and repeat the read-only project-list verification. After successful verification, resume at the pending renderer choice without repeating setup, Objective Confirmation, journey inspection, evidence gathering, or direction approval.
7. If verification still fails, report the exact connection or authorization blocker and continue to offer the Codex visualization route; Stitch remains optional.

Record only the non-secret, review-scoped verification outcome and connection route. Do not add a Design Arc preference field for credentials or connection state. The plugin bundles only the remote connection definition; it does not bundle or republish Google's server code.
