# Design Arc

One Design Arc, available for Codex (live), Claude Code (alpha), and Google Antigravity (alpha).

Design Arc works in three AI coding platforms: Codex, Claude Code, and Google Antigravity. In this documentation, **your AI coding platform** means whichever of those three you are currently using.

Objective: Moving from Subjective Design Opinions to Well Grounded Expert Recommendations

Product feedback is often vague, redesign discussions become subjective, and teams approve attractive screens without knowing whether the complete journey works.
Move from uncertain product feedback to a complete design direction grounded in credible sources.
Design Arc audits the real journey, checks decisions against current first-party platform guidance and inspected real-product journeys, recommends the strongest path, and designs every important state before implementation begins.
### See Design Arc in action
See how Design Arc turns vague feedback into an evidence-backed direction—watch the demo or browse the introduction deck.

| Product walkthrough | Introduction deck |
| --- | --- |
| [![Design Arc product walkthrough thumbnail — opens YouTube](https://img.youtube.com/vi/bbc1t_1LdWk/maxresdefault.jpg)](https://youtu.be/bbc1t_1LdWk) | [![Design Arc introduction deck cover — opens presentation](https://docs.google.com/presentation/d/1EG5vrPC5UqAkNAr9jce0lvZz1Jq5oI4AqAbPVivG2sU/export/png?id=1EG5vrPC5UqAkNAr9jce0lvZz1Jq5oI4AqAbPVivG2sU&pageid=g3fab99837d7_0_185)](https://docs.google.com/presentation/d/1EG5vrPC5UqAkNAr9jce0lvZz1Jq5oI4AqAbPVivG2sU/preview) |
| [Watch on YouTube](https://youtu.be/bbc1t_1LdWk) | [Open presentation](https://docs.google.com/presentation/d/1EG5vrPC5UqAkNAr9jce0lvZz1Jq5oI4AqAbPVivG2sU/preview) |

## Documentation

| Page | What it covers |
| --- | --- |
| [Getting started](docs/getting-started.md) | Simple installation and first use. |
| [Using Design Arc](docs/using-design-arc.md) | The shared workflow, approvals, and everyday review work. |
| [Design Arc for Codex](docs/codex.md) | Codex runtime details: installation, project homes, visuals, and return path. |
| [Design Arc for Claude Code](docs/claude-code.md) | Claude Code runtime details: installation, reminders, visuals, and return path. |
| [Design Arc for Google Antigravity](docs/antigravity.md) | Google Antigravity runtime details: installation, `/design-arc`, local boards, and return path. |
| [Runtime boundaries](docs/runtime-boundaries.md) | What the shared workflow preserves and where platform-specific behavior belongs. |
| [FAQ](docs/faq.md) | Plain-language answers about commands and returning later. |
| [Advanced controls](docs/advanced-controls.md) | Optional commands, graph controls, and technical troubleshooting. |
| [Evidence and methodology](docs/evidence-and-methodology.md) | Evidence modes, complete states, motion, and validation. |
| [Upgrades and migration](docs/upgrades-and-migration.md) | Safe current adapter upgrades and preservation. |
| [Migration history](docs/migration-history.md) | Legacy plugin replacement and versioned recovery instructions. |
| [Trust and sources](docs/trust-limitations-and-sources.md) | Boundaries, limitations, and trusted sources. |

## One product, three platform editions

Choose the edition for the place where you already work. All three editions use the same Design Arc methodology, evidence rules, and approval gates. Codex is the **Live** edition; Claude Code and Google Antigravity are **Alpha** while their newer adapters mature.

| Use | Release status | Choose it when | Start Design Arc |
| --- | --- | --- | --- |
| [**Codex**](docs/codex.md) | **Live** | Your product work already runs in Codex and you want a pinned project home for returning later. | Ask Codex to use Design Arc. |
| [**Claude Code**](docs/claude-code.md) | **Alpha** | Your product work runs in Claude Code and you want an optional project reminder. | Ask Claude Code to use Design Arc. |
| [**Google Antigravity**](docs/antigravity.md) | **Alpha** | Your product work runs in Google Antigravity. | Install it, then use `/design-arc`. |

The product and workflow are shared. Start with Design Arc, then use the runtime page for Codex, Claude Code, or Google Antigravity when installation, saved state, return paths, or visual capabilities differ. See [Codex runtime details](docs/codex.md), [Claude Code runtime details](docs/claude-code.md), [Google Antigravity runtime details](docs/antigravity.md), and [Runtime boundaries](docs/runtime-boundaries.md) for those boundaries.

## You need Design Arc if…

1. Feedback such as “this feels confusing” is just way too vague.
2. Taste is too subjective and not well grounded in expert or user opinions
3. Redesigns improve isolated screens without taking into account the complete user journey

## What Design Arc produces

- A confirmed product objective and the criterion used to judge every finding.
- An audit of the real current journey, including friction, transitions, exits, and non-happy states.
- Evidence appropriate to the product and platform, with current links, limitations, and observed-versus-inferred status.
- One unmistakably recommended direction plus meaningful alternatives, benefits, risks, and trade-offs.
- A complete visual proposal covering entry, transition, loading, empty, error, success, cancellation, and recovery states.
- Decision-ready evidence in your AI coding platform: journey map, key renders, identifiers, validation verdict, gate record, and next authorized owner.

## The workflow

**Rows marked 👤 You show where your involvement may be needed. First-use choices, approval pauses, and the optional Stitch choice are conditional.**

| Workflow step | Platform or source handling it | Human involvement |
| --- | --- | --- |
| Describe the outcome you want | AI coding platform | **👤 You** |
| ↓ | | |
| Choose evidence and approval behavior on first use | AI coding platform | **👤 You — only when no saved preference exists** |
| ↓ | | |
| Audit the current journey | Your website or app + the AI coding platform | |
| ↓ | | |
| Gather and label evidence | Mobbin + the AI coding platform in Guidelines + Benchmarks mode, and official platform guidance + the AI coding platform in Guidelines only mode | |
| ↓ | | |
| Recommend a design direction | AI coding platform | |
| ↓ | | |
| Approve design direction | AI coding platform | **👤 You — only when the selected approval mode pauses here** |
| ↓ | | |
| Validate against platform guidance | Apple, Android, Material, or W3C guidance + the AI coding platform | |
| ↓ | | |
| Decide on any design motion | Relevant official guidance + inspected motion evidence + the AI coding platform | |
| ↓ | | |
| Choose whether to use the optional Stitch workspace | AI coding platform | **👤 You — only if Stitch is recommended** |
| ↓ | | |
| Visualize the complete journey | Static journey board in the AI coding platform by default; optional Google Stitch workspace | |
| ↓ | | |
| Validate every important state | Generated journey screens + the AI coding platform | |
| ↓ | | |
| Approve the visual proposal | AI coding platform | **👤 You — only when the selected approval mode pauses here** |
| ↓ | | |
| Prepare the design handoff | AI coding platform | |

Setup resolves two independent choices: how evidence is gathered and where Design Arc pauses for approval. Every route establishes the objective before inspection or research, audits the actual product, preserves platform rules, and stops at a design-only handoff boundary.

Your AI coding platform produces a consolidated static journey board first, without building disposable app logic. Design Arc recommends the optional Stitch workspace early when one genuine canvas need appears—such as multi-screen editing, visual variants, another-day continuation, collaboration, or export—but you always choose whether to move.

## Install

**Codex — Live:** [Install the Live Codex edition from the OpenAI Plugin Directory](https://chatgpt.com/plugins/plugins_6a82ffefdc88819191f5eaab4eaf116b).

GitHub remains the public source and fallback Codex marketplace. If you need that route, ask Codex to install the Design Arc plugin from https://github.com/friedbeef1/design-arc.

**Ask Claude Code:** Add the Design Arc marketplace from
https://github.com/friedbeef1/design-arc and install `design-arc@design-arc-marketplace`.

**Ask Google Antigravity Desktop:** Install Design Arc globally from
https://github.com/friedbeef1/design-arc

Antigravity CLI is optional. The [Google Antigravity guide](docs/antigravity.md) explains the Desktop-first route and the separate CLI plugin command.

Follow the exact platform commands in [Getting started](docs/getting-started.md). Installation may require download permission.

## Start a review

> Use Design Arc to help me make our onboarding less confusing.

You do not need to remember a command. Ask your AI coding platform for Design Arc by name. Design Arc guides any first-time choices in plain language. Automatic skill selection for an unprefixed request is not guaranteed. The [runtime pages](docs/runtime-boundaries.md) explain the platform-specific ways to return later.
[Learn how to use Design Arc.](docs/using-design-arc.md)

## Trust

Design Arc does not silently redesign, implement, or deploy your product. You choose the objective, evidence approach, and approval behavior.

[Evidence and methodology](docs/evidence-and-methodology.md) · [Trust and sources](docs/trust-limitations-and-sources.md)

## License

[MIT License](LICENSE) · [Privacy](docs/privacy.md) · [Terms](docs/terms.md) · [Support](docs/support.md)
