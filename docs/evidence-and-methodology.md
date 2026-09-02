# Evidence and methodology

[Home](../README.md) · [Getting started](getting-started.md) · [Using Design Arc](using-design-arc.md) · [Codex](codex.md) · [Claude Code](claude-code.md) · [Google Antigravity](antigravity.md) · [FAQ](faq.md) · [Runtime boundaries](runtime-boundaries.md) · [Advanced controls](advanced-controls.md) · [Evidence and methodology](evidence-and-methodology.md) · [Upgrades and migration](upgrades-and-migration.md) · [Migration history](migration-history.md) · [Trust and sources](trust-limitations-and-sources.md)

How are Design Arc recommendations grounded and validated?

## Grounding layers

| Grounding layer | Pain point | How Design Arc solves it | Credible sources used |
| --- | --- | --- | --- |
| Platform requirements | Designs can feel unfamiliar, exclude users, or conflict with platform conventions. | Validate the journey against current guidance for its actual platform. | Apple HIG; Android and Material guidance; W3C web accessibility standards. |
| Product precedent | Teams copy attractive screenshots without understanding the complete journey or failure states. | Inspect relevant end-to-end product journeys and explain why a pattern fits the objective. | Authorized benchmark research through a provider such as Mobbin. |
| Product judgment | Opinions and trade-offs can be presented as if a source proved them. | Tie recommendations to the confirmed objective and label judgment separately from observed evidence. | User-confirmed objective and documented Design Arc synthesis—not an external authority. |
| Visualization and validation | Polished screens can conceal missing transitions, errors, and recovery states. | Visualize the complete journey and inspect every important state before approving it for frontend implementation. | AI coding platform static journey boards by default; optional Google Stitch workspace—not an evidence authority. |
| Relationship context | A correction can miss dependent states when requirements, evidence, and screens are considered separately. | Keep validated relationships visible to plan the smallest compatible correction batch and the regression checks that follow. | The current Design Arc workflow record; the relationship record adds context only. |

First-party guidance remains authoritative for its platform, authorized benchmark evidence remains precedent, the AI coding platform or Stitch provides visualization, and the graph remains relationship context only. A graph relationship is not evidence, proof, approval, a source of requirements, or authority. It is a checked record of relationships already supported by the current workflow, used to see which states may need a compatible repair or regression check. For platform-specific capabilities, use the [runtime boundaries](runtime-boundaries.md) and the relevant runtime page.

### Render conformance and repair

The AI coding platform generates one consolidated static journey board by default, without building disposable application logic. Google Stitch remains an optional external visualizer and persistent editing workspace, not a compliance authority. The AI coding platform compares the complete proposal with the approved direction in a conformance matrix for every material screen and state. It classifies each requirement as `match`, `repairable drift`, `direction decision required`, or `runtime proof`. Only repairable drift is corrected automatically; direction decisions and new authorization stop for the appropriate owner, while runtime proof remains unverified implementation evidence rather than a renderer retry.

Immediately after direction approval and before rendering, Design Arc offers three choices: both the AI coding platform and Stitch (recommended), the AI coding platform only, or Stitch only. It does not wait for a failed or inadequate platform render. The combined route starts both visual surfaces concurrently from the same approved journey while retaining the AI coding platform as the evidence, validation, and approval surface.

The initial proposal may be followed by at most three correction rounds for the whole proposal. Each round batches every known repairable mismatch, generates a new proposal, and reinspects the complete result. That reinspection includes requirements that matched earlier and could have regressed. A written correction is not a corrected proposal; only the inspected replacement render proves the change.

The AI coding platform stops early when two consecutive corrected proposals show no improvement or oscillate, access becomes unavailable, a correction would change direction, or new authorization is required. After the final complete inspection, `meets direction` requires every renderer-expressible requirement to match; otherwise the remaining mismatch scope receives `meets with corrections` or `does not meet`. Prototype review never becomes runtime proof: only the authorized implementation owner can establish that later in staging or on a target device, and the visual verdict does not authorize source implementation, deployment, or release.

The graph can focus correction planning but never replaces complete render inspection or the proposal-wide correction limit. It may help identify a compatible batch, but every replacement still receives the unchanged complete-proposal inspection, including states that previously matched or were unrelated to the correction.

## Choose how Design Arc grounds its recommendations

| Evidence mode | Choose it when | What it means |
| --- | --- | --- |
| **Guidelines + Mobbin benchmarks** — recommended | Inspected real-product journeys would add useful precedent to current platform guidance, and you have an active Mobbin Pro account. | Design Arc inspects complete, relevant journeys, explains why each pattern helps the objective, and records limits. A library listing, popularity, metadata, or one screenshot is never proof of best-in-class quality. |
| **Guidelines only** | You want a first-party-guidance-led review without benchmark research or do not have authorized benchmark access. | Design Arc performs no benchmark lookup and makes no benchmark-evidence claim. It uses current first-party guidance for every affected platform. |

The evidence choice is independent from approval behavior. Design Arc reports the active evidence mode, approval mode, and provenance of each at the start of every run.

Apple Human Interface Guidelines are first-party authority for Apple targets. For Android or web targets, current first-party platform rules override conflicting Apple-inspired judgment. Requirements are kept distinct from product-specific judgment.

Mobbin is the recommended benchmark provider in Guidelines + Benchmarks mode. It remains an external source requiring separate access and authorization; Design Arc does not include or provision the account. If access is missing, Design Arc recommends connecting now, explains Mobbin, guides account creation or sign-in through Mobbin's official site, obtains authorization, and verifies access by inspecting a relevant complete journey. Guidelines only is offered only if connection is declined or verification fails. Design Arc never silently degrades or calls the result benchmark-backed.

Google Stitch is an optional external visualization service requiring separate access and payload authorization. The board supports deeper exploration, while the AI coding platform must still return a reviewable journey map, key renders, identifiers, and validation verdict in its task or session. Apple, Google, Mobbin, and Stitch access is not bundled or official, and none of those services authorizes product-source changes.

## Why each step is crucial

“Performed in / by” names the primary platform, source, or decision-maker. Combined labels show where the AI coding platform orchestrates an external platform or requires a person’s decision.

| Step | Performed in / by | Why it is crucial |
| --- | --- | --- |
| Setup and provenance | AI coding platform + user | Makes the evidence and approval choices independent and records whether each came from the current request, saved preference, confirmed import, or first-use selection. |
| Objective Confirmation | AI coding platform + user | Prevents optimization for the wrong outcome by making the confirmed goal the evaluation criterion. |
| Current-journey audit | AI coding platform, using the supplied website or app | Maps the real entry points, states, friction, transitions, exits, and recovery paths instead of redesigning an imagined product. |
| Evidence gathering | AI coding platform + selected sources | Supplies relevant constraints or inspected precedent without confusing requirements, observations, and product judgment. |
| Direction recommendations | AI coding platform | Makes the strongest journey, alternatives, benefits, risks, and trade-offs decidable before visualization cost is incurred. |
| Direction Gate | User in the AI coding platform, or the active automatic mode | Preserves user control where selected and records why automatic selection is allowed where selected. |
| Full cross-platform validation | AI coding platform + affected-platform first-party guidance | Catches navigation, accessibility, safe-area, and platform conflicts before they are baked into a proposal. |
| Motion specification | AI coding platform + affected-platform guidance + inspected motion evidence | Defines what moves, why, how it behaves, its reduced-motion alternative, and what still requires implementation proof. |
| Complete visual generation | AI coding platform static board by default; optional Google Stitch workspace | Exposes missing transitions and loading, empty, error, success, cancellation, and recovery states across the complete journey without requiring disposable app logic. |
| Inline evidence and render validation | AI coding platform + target device or runtime | Keeps the proposal reviewable in the task or session and prevents attractive output or metadata from becoming a false compliance claim. |
| Visual Proposal Gate | User in the AI coding platform, or Fully automatic after `meets direction` | Separates a validated design proposal from authority to route it, implement it, or release it. Existing 0.3.x records may call this the Stitch Gate. |
| Authorized routing | AI coding platform + authorized Product/Captain/Integration owner | Preserves source, staging, deployment, and release ownership after design approval. |

### Motion grounding and implementation proof

Design Arc specifies material on-screen animations and screen-to-screen transitions before frontend implementation. It first checks the product's existing motion system and standard native behavior, then current first-party platform guidance, actually inspected motion precedent, and finally clearly labeled Design Arc judgment.

Every material motion, including retained native or existing behavior, gets a contract with: Motion ID; journey location; purpose; trigger; start/end state; spatial behavior; choreography; timing; easing/spring; interruption; reduced motion; evidence; provenance; implementation target; implementation source; proof status. Unsupported values are `unverified`.

Static screens or sequences support only start/end state, changing element, journey location, and transition intent; they cannot support exact duration, easing, springs, velocity, interruption, or choreography. Directly applicable native or current first-party specifications and inspected playable evidence can support temporal behavior; otherwise temporal values remain labeled Design Arc judgment or `unverified`.

Stitch prototypes are design evidence, not staging or device implementation proof. When Stitch cannot represent required motion faithfully, Design Arc returns the start and end states plus the motion contract. The authorized implementation owner later builds it with the product's actual stack and validates the result in staging or on the target device.

Each direction explains motion purpose and restraint, relevant precedent and platform guidance, provenance labels, reduced-motion implications, motion-specific risks, implementation complexity, and remaining proof. A visual verdict evaluates the same motion requirements and contract alignment, and `meets direction` records prototype limitations and remaining runtime proof before Fully automatic may continue.

For the nontechnical explanation of what motion evidence can establish, when a recording is needed, and why a prototype is not runtime proof, read [Trusted sources](trusted-sources/README.md) and the [Motion grounding](trusted-sources/motion.md) guide.

Next: [Upgrades and migration](upgrades-and-migration.md).
