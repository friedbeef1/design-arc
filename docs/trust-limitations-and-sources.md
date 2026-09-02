# Trust, limitations and sources

[Home](../README.md) · [Getting started](getting-started.md) · [Using Design Arc](using-design-arc.md) · [Codex](codex.md) · [Claude Code](claude-code.md) · [Google Antigravity](antigravity.md) · [FAQ](faq.md) · [Runtime boundaries](runtime-boundaries.md) · [Advanced controls](advanced-controls.md) · [Evidence and methodology](evidence-and-methodology.md) · [Upgrades and migration](upgrades-and-migration.md) · [Migration history](migration-history.md) · [Trust and sources](trust-limitations-and-sources.md)

What can Design Arc prove, access, implement, or release?

## External evidence and visualization sources

Apple Human Interface Guidelines are first-party authority for Apple targets. For Android or web targets, current first-party platform rules override conflicting Apple-inspired judgment. Requirements are kept distinct from product-specific judgment.

Mobbin can be selected as a benchmark provider in Guidelines + Benchmarks mode. It remains an external source requiring separate access and authorization. Its examples are observed precedent, not a bundled integration or a source to copy. If access is unavailable, Design Arc stops and offers either a one-run Guidelines only fallback or a confirmed saved switch; it never silently degrades or calls the result benchmark-backed.

The AI coding platform—Codex, Claude Code, or Google Antigravity—generates static journey boards by default. Google Stitch is an optional external visualization workspace requiring separate access and payload authorization. Either route must still return a reviewable journey map, key renders, identifiers, and validation verdict in the active task or session. Apple, Google, Mobbin, and Stitch access is not bundled by Design Arc, and none of those services authorizes product-source changes.

Installing any one of the three adapters authorizes only that local adapter installation. Benchmark, browser, visualization, MCP, provider, and product access each require their own authorization, including approval for the data sent. Installing Design Arc never supplies credentials, accepts provider terms, enables a connector, or authorizes product-source changes.

Stitch prototypes are design evidence, not staging or device implementation proof. A prototype can communicate an intended interaction, but it cannot prove runtime quality.

## Relationship assistance boundary

Graph assistance is a project-local relationship record for correction planning, not a new source of truth. It records supported links among the current review's requirements, evidence, screens, states, and checks so Design Arc can plan more precise corrections.

It cannot prove a requirement, establish runtime quality, replace current evidence, or authorize a product decision. Current first-party requirements, accessibility requirements, and inspected evidence always take precedence over a conflicting, stale, inferred, or unsupported relationship.

A failed graph record reduces assistance rather than blocking the review: Design Arc reports the issue and continues the standard workflow. Rebuild uses current authoritative workflow facts for the current review only. Clear requires explicit confirmation for that review's exact record and never removes project preferences, homes, product files, or another review's record.

## Plugin discovery and validation boundary

The Live Codex edition is published in the OpenAI Plugin Directory. [Open the Design Arc listing](https://chatgpt.com/plugins/plugins_6a82ffefdc88819191f5eaab4eaf116b). GitHub remains the public source, the fallback Codex marketplace, and the installation source for the Claude Code and Google Antigravity Alpha editions.

Deterministic tests protect the written workflow contract, but they do not prove every future runtime response. They verify package structure and reject known contract violations; current-task inspection and evidence are still required before any design, implementation, staging, or release claim.

## Claude Code, Claude Desktop, and MCP

Design Arc 1.5.4 is packaged and verified for Claude Code. Its Claude package contains one skill and no agents, hooks, MCP servers, or LSP servers. The namespaced slash command and `.claude` project state belong to Claude Code.

It is not a Claude Desktop chat extension and does not install or configure a Desktop MCP server. Claude Desktop’s Code surface may share Claude Code plugin settings, but this release does not claim Desktop visual or interaction QA. Claude Desktop chat MCP configuration is separate from Claude Code configuration. An MCP that happens to be configured in either product is still external to Design Arc and requires its own access, authentication, tool-use, and payload authorization.

For platform details, use [Anthropic’s Claude Code Desktop guide](https://code.claude.com/docs/en/desktop) and [Anthropic’s MCP guide](https://code.claude.com/docs/en/mcp) as secondary references. Design Arc’s own package inventory and authorization boundary above remain the release contract.

## Evidence, implementation, and release boundaries

Design Arc must not claim current product inspection, first-party guidance, benchmark evidence, new generated output, exact render dimensions, accessibility, safe-area behavior, native/browser behavior, or physical-device compliance without corresponding current-task proof.

A validated visual journey remains a design proposal. No evidence mode, approval mode, external-service access, provider authorization, Direction decision, or visual verdict authorizes source implementation, staging, deployment, live release, destructive or provider changes, or work outside the authorized integration lane. Those actions require their own scope, owner, authorization, and evidence.

For the complete source library, see [Trusted sources](trusted-sources/README.md). For shared and platform-specific limits, see [Runtime boundaries](runtime-boundaries.md).

## Trademarks

Apple, Google, Mobbin, and Stitch are trademarks of their respective owners. Design Arc is not affiliated with or endorsed by those owners, and no official integration is claimed.

Next: [Home](../README.md).
