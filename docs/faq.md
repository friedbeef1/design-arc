# Frequently asked questions

[Home](../README.md) · [Getting started](getting-started.md) · [Using Design Arc](using-design-arc.md) · [Codex](codex.md) · [Claude Code](claude-code.md) · [Google Antigravity](antigravity.md) · [FAQ](faq.md) · [Runtime boundaries](runtime-boundaries.md) · [Advanced controls](advanced-controls.md) · [Evidence and methodology](evidence-and-methodology.md) · [Upgrades and migration](upgrades-and-migration.md) · [Migration history](migration-history.md) · [Trust and sources](trust-limitations-and-sources.md)

Use the short answers below, then follow the relevant guide when you want the full explanation.

[Getting started](#getting-started) · [Evidence](#evidence-and-recommendations) · [Approvals](#approvals-and-automation) · [Screens and Stitch](#screens-visual-proposals-and-stitch) · [Projects and platforms](#projects-and-ai-coding-platforms) · [Installation and support](#installation-upgrades-privacy-and-support)

## Getting started

| Question | Short answer | Full explanation |
| --- | --- | --- |
| **What is Design Arc?** | An evidence-grounded workflow for turning uncertain product feedback into a complete, reviewable design direction. | [What Design Arc produces](../README.md#what-design-arc-produces) |
| **Do I need to remember a Design Arc command?** | No. Ask Codex, Claude Code, or Google Antigravity to use Design Arc in ordinary language. | [Start a review](using-design-arc.md#start-a-review-in-ordinary-language) |
| **Which edition should I use?** | Use Design Arc in the AI coding platform where you already do the product work. | [Compare the three editions](../README.md#one-product-three-platform-editions) |
| **Can I use Design Arc with an existing product?** | Yes. It begins by auditing the real current journey rather than assuming a blank-slate redesign. | [What happens next](getting-started.md#what-happens-next) |
| **What does Design Arc ask me first?** | It confirms the outcome you want before inspecting or researching anything. | [Approval and trust controls](using-design-arc.md#approval-and-trust-controls) |
| **Does Design Arc implement the design?** | No. It ends with a design handoff unless implementation receives separate authorization. | [Implementation and release boundary](runtime-boundaries.md#implementation-and-release-boundary) |

## Evidence and recommendations

| Question | Short answer | Full explanation |
| --- | --- | --- |
| **What is Guidelines only mode?** | It uses applicable first-party platform guidance without benchmark research or benchmark claims. | [Choose the evidence approach](evidence-and-methodology.md#choose-how-design-arc-grounds-its-recommendations) |
| **What is Guidelines + Benchmarks mode?** | It combines applicable official guidance with inspected, authorized real-product journeys. | [Choose the evidence approach](evidence-and-methodology.md#choose-how-design-arc-grounds-its-recommendations) |
| **Is Mobbin required?** | No. Mobbin is an optional benchmark provider used only when Guidelines + Benchmarks mode is selected and access is authorized. | [External evidence sources](trust-limitations-and-sources.md#external-evidence-and-visualization-sources) |
| **Does Apple guidance apply to every product?** | No. Apple guidance governs Apple targets; Android, Material, or W3C guidance takes precedence for those platforms. | [Grounding layers](evidence-and-methodology.md#grounding-layers) |
| **Why use official guidance and benchmark evidence together?** | Guidance supplies platform requirements; inspected journeys supply product precedent. Design Arc labels those separately from its own judgment. | [Evidence and methodology](evidence-and-methodology.md) |
| **Does a popular screenshot prove a pattern is best?** | No. Design Arc inspects relevant complete journeys and important states instead of treating popularity or one screen as proof. | [Guidelines + Benchmarks](evidence-and-methodology.md#choose-how-design-arc-grounds-its-recommendations) |
| **What is graph assistance?** | An optional local relationship map that helps trace requirements, evidence, screens, and regression checks. | [Graph-assisted corrections](using-design-arc.md#graph-assisted-corrections) |
| **Does the graph prove that a design is correct?** | No. It supports reasoning but never replaces evidence, platform guidance, approval, or complete screen inspection. | [Relationship assistance boundary](trust-limitations-and-sources.md#relationship-assistance-boundary) |
| **Can Design Arc guarantee compliance?** | No. It can check the written proposal against evidence and guidance, but implementation and device proof happen later. | [Evidence and release boundaries](trust-limitations-and-sources.md#evidence-implementation-and-release-boundaries) |

## Approvals and automation

| Question | Short answer | Full explanation |
| --- | --- | --- |
| **What is Objective Confirmation?** | The user-confirmed outcome that every finding and recommendation must serve. | [Approval and trust controls](using-design-arc.md#approval-and-trust-controls) |
| **What is the Direction Gate?** | The point where the recommended journey direction is approved or automatically selected under the chosen mode. | [Approval modes](using-design-arc.md#approval-and-trust-controls) |
| **What is the Visual Proposal Gate?** | The point where the complete validated screen proposal is approved; older records may call it the Stitch Gate. | [Approval modes](using-design-arc.md#approval-and-trust-controls) |
| **Which approval mode is recommended?** | Guided is the safest default for a new project because it pauses at both key decisions. | [Approval modes](using-design-arc.md#approval-and-trust-controls) |
| **Can Design Arc follow its recommendation automatically?** | Yes. Follow recommendation continues past the Direction Gate but still pauses for the visual proposal. | [Approval modes](using-design-arc.md#approval-and-trust-controls) |
| **Can I bypass both approval gates?** | Yes, for one run through Fully automatic mode, but the request must still provide an explicit objective. | [Approval modes](using-design-arc.md#approval-and-trust-controls) |
| **Does Fully automatic authorize implementation or deployment?** | No. It changes approval pauses only; source changes, staging, deployment, and release remain separately authorized. | [Implementation and release boundary](runtime-boundaries.md#implementation-and-release-boundary) |
| **What happens after three unsuccessful correction rounds?** | Design Arc stops, flags every unresolved mismatch, and records the attempted corrections instead of silently continuing. | [What happens after screens render](using-design-arc.md#what-happens-after-screens-render) |

## Screens, visual proposals, and Stitch

| Question | Short answer | Full explanation |
| --- | --- | --- |
| **What visual output does Design Arc create first?** | One complete static journey board covering the important entry, transition, loading, empty, error, success, cancellation, and recovery states. | [Choosing the visual workspace](using-design-arc.md#choosing-your-ai-coding-platform-or-stitch-for-the-screens) |
| **Does Codex build an app just to show the screens?** | No. Codex creates static screens and journey boards without disposable application logic. | [Design Arc for Codex](codex.md#what-codex-adds) |
| **What can Claude Code create visually?** | It can prepare HTML/CSS, SVG, specifications, and lightweight boards; it does not claim native image generation. | [Design Arc for Claude Code](claude-code.md#what-claude-code-adds) |
| **What can Google Antigravity create visually?** | It can prepare lightweight boards and specifications, while polished editable mockups are a strong reason to consider Stitch. | [Design Arc for Google Antigravity](antigravity.md#what-google-antigravity-adds) |
| **Is Google Stitch required?** | No. Stitch is optional and separately authorized. | [Choosing the visual workspace](using-design-arc.md#choosing-your-ai-coding-platform-or-stitch-for-the-screens) |
| **When will Design Arc recommend Stitch?** | When a persistent canvas materially helps with visual alternatives, multi-screen editing, refinement, collaboration, continuity, or export. | [Visualization sources](trusted-sources/visualization.md) |
| **Can I continue in my AI coding platform instead of Stitch?** | Yes. A Stitch recommendation is advisory, and you choose whether to move. | [Choosing the visual workspace](using-design-arc.md#choosing-your-ai-coding-platform-or-stitch-for-the-screens) |
| **What happens when I choose Both?** | The initial platform board and Stitch workspace start concurrently from the same approved specification. After comparing them independently, you choose whether to refine the platform version, the Stitch version, or both. | [Choosing the visual workspace](using-design-arc.md#choosing-your-ai-coding-platform-or-stitch-for-the-screens) |
| **Can Design Arc review changes made later in Stitch?** | Yes, when the updated screens are retrieved or supplied; Design Arc compares them with the approved requirements before accepting them. | [Choosing the visual workspace](using-design-arc.md#choosing-your-ai-coding-platform-or-stitch-for-the-screens) |
| **Does a polished Stitch board prove correctness?** | No. Stitch visualizes the proposal; your AI coding platform still validates the returned screens and important states. | [Visualization and validation](trusted-sources/visualization.md) |
| **Does Design Arc include a Stitch or Mobbin MCP server?** | No. Any MCP, browser, or manual access path must be separately installed, configured, named, and authorized. | [External evidence sources](trust-limitations-and-sources.md#external-evidence-and-visualization-sources) |

## Projects and AI coding platforms

| Question | Short answer | Full explanation |
| --- | --- | --- |
| **Are the Codex, Claude Code, and Google Antigravity editions different products?** | No. They are platform packages for one Design Arc methodology. | [Runtime boundaries](runtime-boundaries.md) |
| **What is a Codex project home?** | An optional pinned Codex task that gives one product a visible place to return to Design Arc later. | [Returning later in Codex](codex.md#returning-later) |
| **Does Claude Code create a project home?** | No. Claude Code can add one approved, clearly delimited reminder to `CLAUDE.md` instead. | [Returning later in Claude Code](claude-code.md#returning-later) |
| **How do I return in Google Antigravity?** | Open the product project and ask for Design Arc by name; `/design-arc` is available where that surface has loaded the skill. | [State and returning later](antigravity.md#state-and-returning-later) |
| **Do Codex, Claude Code, and Google Antigravity share project state?** | No. Preferences, active reviews, graphs, homes, reminders, and upgrade lifecycles remain separate. | [What remains separate](runtime-boundaries.md#what-remains-separate) |
| **Can I continue the same active review in another AI coding platform?** | No. Start a new review there; Design Arc never silently merges or resumes active review records across runtimes. | [What remains separate](runtime-boundaries.md#what-remains-separate) |
| **Can I use Design Arc for multiple products?** | Yes. Each product keeps separate project-scoped state and, in Codex, at most one approved project home. | [Saved state and upgrades](advanced-controls.md#saved-state-and-upgrades) |

## Installation, upgrades, privacy, and support

| Question | Short answer | Full explanation |
| --- | --- | --- |
| **Do I install Design Arc for every project?** | No. Install the edition once for the relevant AI coding platform; each participating project completes its own first-use setup. | [Install once](getting-started.md#install-once) |
| **Do I need to install all three editions?** | No. Install only the Codex, Claude Code, or Google Antigravity edition you intend to use. | [Installation choices](getting-started.md) |
| **Are the three edition upgrades independent?** | Yes. Updating one adapter does not update or rewrite another platform’s installation or project state. | [Current adapter upgrades](upgrades-and-migration.md#current-adapter-upgrades) |
| **Will an upgrade disturb existing projects?** | It should not. Upgrade validation preserves preferences, return paths, product files, reviews, graphs, and active work. | [Upgrade preservation](upgrades-and-migration.md) |
| **Can I import portable preferences from another edition?** | Only through the documented one-time, confirmed import path; active reviews and runtime records are never merged. | [Runtime-specific import rules](runtime-boundaries.md#what-remains-separate) |
| **Does installing Design Arc authorize Mobbin, Stitch, browsers, or MCPs?** | No. Every external service and payload requires separate access and authorization. | [Trust and external sources](trust-limitations-and-sources.md#external-evidence-and-visualization-sources) |
| **Where does Design Arc store project information?** | In platform-specific local project paths such as `.codex/`, `.claude/`, or `.gemini/`, as documented for each edition. | [Privacy](privacy.md) |
| **Should review graphs be committed to Git?** | The project owner decides. Design Arc does not silently change `.gitignore` or treat graph records as product source. | [Graph controls](advanced-controls.md#graph-assistance-matrix) |
| **Where can I report a problem?** | Use the public GitHub issue tracker after removing credentials and confidential product evidence. | [Support](support.md) |

Still unsure? Start with [Getting started](getting-started.md), then ask Design Arc the question in ordinary language.
