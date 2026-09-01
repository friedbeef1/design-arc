# Using Design Arc

[Home](../README.md) · [Getting started](getting-started.md) · [Using Design Arc](using-design-arc.md) · [Codex](codex.md) · [Claude Code](claude-code.md) · [Google Antigravity](antigravity.md) · [FAQ](faq.md) · [Runtime boundaries](runtime-boundaries.md) · [Advanced controls](advanced-controls.md) · [Evidence and methodology](evidence-and-methodology.md) · [Upgrades and migration](upgrades-and-migration.md) · [Migration history](migration-history.md) · [Trust and sources](trust-limitations-and-sources.md)

How do I use Design Arc after installation?

## Start a review in ordinary language

Describe the product outcome you want in ordinary language. For example: “Use Design Arc to help me make our onboarding less confusing.” Explicitly asking Codex, Claude Code, or Google Antigravity to use Design Arc invokes it directly.

Commands are optional shortcuts, not required knowledge.

If your AI coding platform selects Design Arc for a suitable request that did not invoke it directly, it asks for permission before beginning. Until you approve, it does not start setup, inspect your product, gather Design Arc evidence, or create Design Arc project or review records. Automatic skill selection is not guaranteed, so ask for Design Arc by name when certainty matters. Runtime-specific return paths are described in the [Codex runtime](codex.md), [Claude Code runtime](claude-code.md), and [Google Antigravity runtime](antigravity.md) pages. Design Arc does not run continuously or silently in every task.

Codex, Claude Code, or Google Antigravity may offer Design Arc for requests such as:

- “Help me make our onboarding less confusing.”
- “Audit how customers complete checkout and propose a better complete journey.”
- “Redesign account recovery so people can get back in without weakening security.”

Natural-language requests such as “use Guidelines only for this run” or “follow your recommendation this time” are one-run overrides; they do not rewrite the saved project preference.

The workflow, evidence rules, approval modes, renderer choice, and design-only handoff boundary are shared. Invocation, saved preferences, active-review records, return paths, and adapter upgrades are platform-specific. Codex, Claude Code, and Google Antigravity never merge, migrate, resume, or continue an active review across runtimes. Runtime-specific installation, invocation, saved state, returning later, visual capabilities, and upgrades belong to the [Codex runtime](codex.md), [Claude Code runtime](claude-code.md), and [Google Antigravity runtime](antigravity.md) pages. [Runtime boundaries](runtime-boundaries.md) explains why these details stay separate.

## Return to a project

The return path is a runtime detail. Use [Design Arc for Codex](codex.md) for Codex project homes, [Design Arc for Claude Code](claude-code.md) for Claude Code re-entry and its optional reminder, and [Design Arc for Google Antigravity](antigravity.md) for Antigravity re-entry. A runtime-specific return path never merges or continues a review from another runtime.

## Choosing your AI coding platform or Stitch for the screens

Design Arc generates one complete static journey board in your AI coding platform by default. It does not build disposable application logic merely to visualize the proposal. The board covers every important state, while separate high-resolution screens are generated only when closer inspection or a focused correction needs them.

Stitch is optional and Design Arc recommends it when any one genuine canvas trigger occurs. Triggers include a second meaningful visual direction, changes across three or more screens, precise visual iteration, self-editing, another-day continuation, a board becoming difficult to review, unrelated drift after one platform correction round, device variants, collaboration, or design export.

The first recommendation explains the specific benefit and offers three numbered choices: Stitch (recommended), stay in your AI coding platform, or both. You can reply with `1`, `2`, or `3`. You can stay in your AI coding platform. Choosing both creates the platform board and Stitch workspace from the same approved journey while the AI coding platform remains the evidence, validation, and approval surface. Design Arc may recommend Stitch again, briefly, only after another genuine trigger or materially larger scope. A Stitch recommendation is advisory and never transfers the proposal automatically. A stay choice applies to the current editing phase; Design Arc may ask again if the work materially grows. If you say not to recommend Stitch again for this review, Design Arc suppresses every further recommendation for that review.

When you choose both, Design Arc starts the AI coding platform board and Stitch workspace concurrently from the same approved specification. It waits for both initial renders before correcting either one. Each render is then checked independently against the approved specification before the pair is compared. Both share one limit of three proposal-wide correction rounds; they do not receive three rounds each. If either initial render fails, Design Arc reports that the comparison is incomplete and asks before continuing with only one renderer.

When you choose Stitch, Design Arc preserves the approved requirements and compares the latest retrieved or supplied Stitch changes before accepting them as the current proposal. Stitch access—including an exact Stitch MCP when actually configured—remains separately authorized. Design Arc itself bundles no MCP.

## What happens after screens render

Design Arc corrects straightforward visual drift before asking you to approve the visual proposal. The initial proposal may be followed by at most three correction rounds for the whole proposal. Each round batches every known repairable mismatch, generates a new proposal, and reinspects the complete result. The same validation and correction rules apply whether your AI coding platform or Stitch renders the screens.

If the proposal still does not match, Design Arc stops and flags every unresolved mismatch and the attempts already made. It asks sooner only when the correction would change the approved direction, requires new authorization, or cannot be proven in a prototype.

## Approval and trust controls

> Design Arc does not silently redesign, implement, or deploy your product. You choose the objective, evidence approach, and approval behavior.

Objective Confirmation establishes the product outcome before the audit or evidence gathering begins. The Direction Gate confirms the recommended design direction; the Visual Proposal Gate confirms the validated visual proposal. Existing 0.3.x review records may call this the Stitch Gate; it is the same gate, not an additional approval.

| Approval mode | Objective | Visual Proposal Gate |
| --- | --- | --- |
| **Guided** — recommended for a new project | Confirm; stop at Direction Gate | Stop for approval |
| **Follow recommendation** | Confirm; continue at Direction Gate with the visibly marked recommendation | Stop for approval |
| **Fully automatic** | The current request must state an explicit objective; continue at Direction Gate with the visibly marked recommendation | Continue only after a `meets direction` verdict |

“Follow your recommendation” is a one-run Follow recommendation alias. “Bypass both gates” is a one-run Fully automatic alias, but it never permits Design Arc to invent a missing objective. Automatic modes change decision pauses, not the audit, evidence, complete-state, validation, or ownership requirements.

## Graph-assisted corrections

Design Arc understands how requirements, evidence and screens affect one another, helping it make more precise corrections without surrendering approval control.

Graph assistance is active by default for every new 0.3.0 review in both existing and new projects when no project or platform-local safety control turns it off. That default does not rewrite project preferences or platform-local settings. An active review remains exactly as it started; its next clean review gains the 0.3.0 assistance.

Graph assistance adds no approval gate. Objective Confirmation, the Direction Gate, the Visual Proposal Gate, the active approval mode, and the full review of every important state remain exactly the same.

The loop controls what happens and when Design Arc stops. The relationship map helps Design Arc understand what each correction affects; it advises the loop but never replaces it.

```mermaid
flowchart TD
    A["Confirm the user’s objective<br/>You + AI coding platform"] --> B["Inspect the current journey<br/>Your website or app + AI coding platform"]
    B --> C{"Select evidence mode<br/>AI coding platform; You when a choice is required"}
    C -- "Guidelines only mode" --> C1["Official Apple Human Interface Guidelines for Apple,<br/>Android and Material guidance for Android,<br/>or W3C guidance for web + AI coding platform"]
    C -- "Guidelines + Benchmarks mode" --> C2["Mobbin journey benchmarks + applicable<br/>official platform guidance + AI coding platform"]
    C1 --> D["Build the relationship map<br/>Platform-local graph record"]
    C2 --> D

    D --> E["Recommend a design direction<br/>AI coding platform"]
    E --> F["Direction approval<br/>You + AI coding platform"]
    F --> G["Generate one complete static journey board<br/>AI coding platform by default"]
    G -. "Canvas trigger + user chooses Stitch" .-> GS["Continue in an editable workspace<br/>Google Stitch + AI coding platform"]
    GS --> H

    G --> H["Inspect every important state<br/>Generated screens + AI coding platform"]
    H --> I{"Anything incorrect?<br/>AI coding platform verdict"}

    I -- "No" --> J["Final verdict<br/>AI coding platform"]
    I -- "Yes" --> K["Find affected requirements, screens and states<br/>AI coding platform relationship-map reasoning"]
    K --> L["Prepare one proposal-wide correction batch<br/>AI coding platform"]
    L --> M["Send corrections to the active renderer<br/>AI coding platform, or Google Stitch + AI coding platform"]
    M --> H

    J --> N["Visual proposal approval<br/>You + AI coding platform"]
    L -. "Maximum three correction rounds" .-> J
```

Official Apple guidance governs Apple platform requirements; the applicable first-party guidance does the same for Android or web. Mobbin supplies product precedent only in Guidelines + Benchmarks mode.

Before Stitch is used, your AI coding platform prepares the complete evidence-grounded journey, requirements, and important-state inventory. Stitch visualizes rather than establishes correctness; your AI coding platform validates the returned screens and applies the same proposal-wide correction loop of up to three rounds. Stitch remains optional and separately authorized. For platform-specific visual capabilities and recommendation details, use the [Codex runtime](codex.md), [Claude Code runtime](claude-code.md), or [Google Antigravity runtime](antigravity.md) page.

Design Arc bundles no MCP server, so the generic diagram does not invent a connection that is not configured. Mobbin and Google Stitch are external services, not automatically available to your AI coding platform. Google now provides an official Stitch MCP server and SDK, but Design Arc uses that route only when it is separately installed, configured, and authorized. When a particular review actually uses an MCP, its run record and evidence labels name the exact configured MCP server or tool; otherwise they name the browser or manual access path used. Design Arc does not imply an official Mobbin MCP integration.

Graph assistance is optional internal reasoning support. If it is unavailable or turned off, Design Arc continues the same review without it. It never replaces evidence, platform guidance, approvals, or complete screen inspection. People who want to inspect or manage it can use the commands in [Advanced controls](advanced-controls.md).

Next: [Evidence and methodology](evidence-and-methodology.md).
