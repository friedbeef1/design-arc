---
name: design-arc
description: Use when a mobile or web product journey feels confusing, incomplete, inconsistent, or subject to taste-based redesign debate, or when a team needs evidence-backed directions and complete material states before implementation.
user-invocable: true
---

## Google Antigravity entry point

Use `/design-arc` to begin a Design Arc journey review. This root extension
contains one self-contained skill and does not declare agents, hooks, MCP
servers, or external-service connectivity. External tools and services remain
separately authorized.

The same `/design-arc` workflow is supported in Google Antigravity standalone,
IDE, and CLI surfaces when that surface has loaded this extension. Do not claim
that another surface was exercised unless it was actually used. Keep normal
onboarding command-light: storage, graph controls, and technical commands are
secondary to the journey review.

## Google Antigravity project setup and re-entry

On new Google Antigravity setup, propose every missing preference and obtain explicit confirmation before creating `.gemini/design-arc.yaml`.

When `.gemini/design-arc.yaml` already exists, treat it as the Antigravity saved preference, do not offer a cross-runtime import, and never overwrite it from `.codex/design-arc.yaml` or `.claude/design-arc.yaml`.

Every Antigravity-created `.gemini/design-arc-active-review.json` and review artifact under `.gemini/design-arc/reviews/<review_id>/` records `runtime: antigravity` together with its pinned `workflow_version`; reject a `.gemini` record labelled `runtime: codex` and do not reinterpret it.

Only when the Antigravity preference is absent, inspect
`.codex/design-arc.yaml` and `.claude/design-arc.yaml` read-only when they
exist. For each source independently, the portable fields are `evidence_mode`,
`benchmark_provider` when valid for Guidelines + Benchmarks, `approval_mode`,
and `graph_assistance`; validate the complete portable mapping before proposing
an import. Source-specific homes, reminders, active reviews, review artifacts,
graphs, task identities, and session context are not portable. Show the
proposed values and identify ignored source-specific fields without exposing
unrelated contents.

If both source preference files exist, show the separately validated portable proposals and require the user to choose exactly one source before asking for import approval; never merge them.
Only after explicit import approval, copy the validated portable values from the chosen source into a new Antigravity preference file; do not move or rename the source file.
Treat every Codex and Claude preference file, active-review record, review artifact, graph, home record, reminder, task identity, and session context as read-only; verify the chosen source remains byte-for-byte unchanged.
If the user declines import or declines to choose a source, leave all Codex and Claude state untouched and continue with a fresh Antigravity setup.
If either inspected source file is malformed or any portable value is invalid, import nothing from that source, report the invalid fields without exposing unrelated contents, and offer fresh Antigravity setup or the other separately valid source.

Never tell a Google Antigravity user to pass work to Codex or Claude Code unless the user explicitly requests a cross-platform handoff. A cross-platform handoff is an explicit user choice, not an import side effect: do not transfer, merge, alter, or resume source reviews, tasks, sessions, or runtime state.

Graph assistance never bypasses Objective Confirmation.
Graph assistance never bypasses Direction Gate.
Graph assistance never bypasses Visual Proposal Gate.
Graph assistance never weakens Objective Confirmation, Direction Gate, or Visual Proposal Gate approval-mode behavior.

### Safe Google Antigravity plugin upgrade

An upgrade or downgrade changes the Google Antigravity extension, not a
participating product and not the Codex or Claude Code adapters. Before changing
an installed extension, report the installed and requested versions, source,
and exact route; require confirmation unless the current request already
authorizes that exact change. Re-read installed state afterward instead of
trusting command success, and use only a supported Google Antigravity route.

Do not run project setup, edit `.gemini/design-arc.yaml`, touch product files,
or continue an active review during an adapter change. Compare the participating
Antigravity preferences, active-review records, review directories, and graphs
byte-for-byte before and after. If any changed, stop and report the exact
affected project; never rewrite project state automatically. An already-open
Google Antigravity session retains its pinned runtime and workflow version. Do
not force-close, convert, merge, or resume it as part of an upgrade or
downgrade; start a new clean session to load the changed adapter version.

# Design Arc

Turn an explicit product outcome into a complete, evidence-backed journey proposal. Audit the real experience, compare meaningful directions, recommend one path, and visualize every material state while preserving the user's approval and release boundaries.

## Non-negotiable order

Resolve setup before product inspection, external research, or generation. Then establish the user's objective before any of those activities.

Use this state machine:

`setup → objective → current-journey audit → evidence → directions → Direction Gate → full first-party validation → complete visual journey → render validation → Visual Proposal Gate → authorized handoff`

Setup controls how evidence is gathered and where approval pauses occur. It never lowers evidence quality.

## Setup and project preference

Store project-scoped choices in `.gemini/design-arc.yaml`:

```yaml
evidence_mode: benchmarks
benchmark_provider: mobbin
approval_mode: guided
graph_assistance: on
```

Valid evidence modes are `benchmarks` and `guidelines`; retain these saved values for backward compatibility. Present them to users as **Guidelines + Benchmarks** and **Guidelines only**. `benchmark_provider` is valid only with Guidelines + Benchmarks; currently document `mobbin` when the user chooses that external provider. Valid approval modes are `guided`, `follow-recommendation`, and `fully-automatic`. Do not create a global preference.

### Commands

- `/design-arc setup` — resolve migration and any missing project choices.
- `/design-arc upgrade` — safely upgrade the Google Antigravity plugin while preserving preferences, reminders, reviews, graphs, product files, and active sessions.
- `/design-arc evidence benchmarks` — save Guidelines + Benchmarks for this project after confirming provider access.
- `/design-arc evidence guidelines` — save Guidelines only and omit `benchmark_provider`.
- `/design-arc mode` — report the saved and active approval mode and provenance.
- `/design-arc mode guided` — save Guided.
- `/design-arc mode follow-recommendation` — save Follow recommendation.
- `/design-arc mode fully-automatic` — save Fully automatic.

Graph controls are `/design-arc graph`, `/design-arc graph on`, `/design-arc graph off`, `/design-arc graph explain`, `/design-arc graph rebuild`, `/design-arc graph clear`, `/design-arc graph global off`, and `/design-arc graph global on`.

- `/design-arc graph` — report the current review's resolved graph state and provenance without changing it.
- `/design-arc graph on` or `/design-arc graph off` — save only this project's graph setting.
- `/design-arc graph explain` — report how the state resolved and whether the current graph is usable.
- `/design-arc graph rebuild` — reconstruct only the current review's graph from current authoritative workflow evidence.
- `/design-arc graph clear` — request deletion of only the current review's graph under the confirmation rule below.
- `/design-arc graph global off` or `/design-arc graph global on` — save only the laptop/profile safety state; global on never overrides project off.

A natural-language request such as “use Guidelines only for this run” or “follow your recommendation this time” is a one-run override, not permission to rewrite the file. A setting command explicitly authorizes changing only that named project preference.

Equivalent natural-language requests activate the same graph report, one-review override, project setting, explanation, rebuild, clear, or laptop-global safety flow without requiring command syntax. Distinguish “for this review” from “for this project” and “on this laptop”; when scope is materially ambiguous, ask before saving or deleting anything.

Treat Design Arc as directly invoked when the current request includes `/design-arc` or explicitly asks to use Design Arc by name. In those cases, begin without a separate activation question and resolve setup and the objective in the required order before doing product work.

If Google Antigravity has selected this skill for a suitable request that did not directly invoke Design Arc, ask for the user's approval before beginning Design Arc. Explain briefly why the request appears suitable and wait for an affirmative response. Before approval, do not resolve Design Arc setup, inspect the product, gather evidence, create preferences or write review records. If the user declines, continue with the ordinary request without Design Arc and do not imply that its workflow or evidence controls were applied. Skill selection is not guaranteed for an unprefixed request, so never claim that Design Arc reviewed work unless this skill actually loaded.

A request such as “upgrade Design Arc” activates this same safe upgrade flow without requiring the command.

### Runtime state and adapter isolation

Codex stores preferences at `.codex/design-arc.yaml`, active-review identity at
`.codex/design-arc-active-review.json`, and review artifacts under
`.codex/design-arc/reviews/<review_id>/`. Google Antigravity stores preferences only at `.gemini/design-arc.yaml`, active-review identity only at `.gemini/design-arc-active-review.json`, and review artifacts only under `.gemini/design-arc/reviews/<review_id>/`.

Every new active-review record includes `runtime: codex` or `runtime: antigravity` together with its pinned `workflow_version`.
An existing active record without runtime provenance remains owned by the
runtime-specific path where it was created; do not rewrite it merely to add the
field. Each adapter reads and writes only its own preference, active-review,
review, and graph paths.

Never import, merge, migrate, resume, or continue an active review across runtimes; preference import is the only allowed cross-runtime copy.
Cross-runtime preference import copies only explicitly confirmed portable
preference values into a new destination-runtime file. It never copies a Codex
home, reminder, active-review record, review artifact, graph, task identity, or
session context.

An adapter upgrade or downgrade preserves both runtimes' preferences, reminder blocks, review directories, graph files, product files, and active-review records byte-for-byte.
It never resumes, converts, merges, or rewrites an active session; that session retains its recorded runtime and workflow version, while only a new clean session may load the changed adapter version.
An older adapter ignores unsupported state while preserving it; it never deletes or reinterprets newer preferences, reminders, reviews, or graphs.

### Resolution precedence

Resolve evidence and approval independently, in this order:

1. Explicit one-run override in the current request; do not save it unless asked.
2. Saved `.gemini/design-arc.yaml` value.
3. Confirmed Codex preference import, only when the Antigravity file is absent.
4. First-use selection for every choice still missing.

Always report the active evidence mode and approval mode, and the provenance of each independently. Use one of: current-request one-run override, saved Design Arc preference, confirmed Codex preference import, or first-use selection. Never attribute an overridden value to the saved file.

Collect first-use evidence and approval choices in two separate user turns. Never present both choice lists in the same message.

**Step 1 — evidence.** Present exactly this numbered choice first:

1. **Guidelines + Mobbin benchmarks — recommended.** Use inspected real-product journeys plus current first-party guidance. Ensure you have an active Mobbin Pro account before choosing this option; Design Arc does not include or provision the account.
2. **Guidelines only.** Use current first-party platform guidance without benchmark research.

Ask the user to reply with `1` or `2`. Accept an unambiguous free-form selection, but make the numeric reply the default. Resolve and record the evidence choice before continuing.

**Step 2 — approval.** Only after evidence is resolved, present this separate numbered choice:

1. **Guided — recommended for a new project.** Stop at Objective Confirmation, Direction Gate, and Visual Proposal Gate.
2. **Follow recommendation.** Stop at Objective Confirmation, automatically select the marked direction, and stop at Visual Proposal Gate.
3. **Fully automatic.** Continue only from an explicit current-request objective, select the marked direction, and pass Visual Proposal Gate only on `meets direction`.

Ask the user to reply with `1`, `2`, or `3`. Accept an unambiguous free-form selection, but make the numeric reply the default. Before saving first-use choices, state the proposed file values and obtain confirmation.

### Graph assistance for 0.3.0 reviews

Design Arc 0.3.0 may maintain a validated project-local relationship record to plan more precise corrections. The authoritative setup, objective, evidence, direction, visualization, and repair workflow remains unchanged.

#### Resolution and review identity

Save the project setting only as `graph_assistance: on|off` in that project's `.gemini/design-arc.yaml`; keep laptop-global graph safety state isolated under the active Google Antigravity profile, never in a project or product file. The profile state is a safety control shared by this Google Antigravity installation, not a design preference and not a source of project truth.

Read laptop-global safety only from `<resolved Google Antigravity profile root>/design-arc-global.yaml`, whose root mapping uses `schema: design-arc.global/v1` and `graph_assistance_ceiling: on|off`; no other path or field controls the laptop ceiling. Additional mapping entries are forward-compatible state owned by later Design Arc versions and are ignored by 0.3.0 resolution.

When the global file is absent, treat the ceiling as on without creating it; malformed YAML, a non-mapping root, a missing or unsupported schema, or a missing or invalid ceiling fails safe as global off, is reported, and is never rewritten merely by resolution.

A confirmed global command changes only `graph_assistance_ceiling`, preserves the valid schema and every unrelated mapping entry, writes a same-directory temporary file with mode `0600`, flushes and fsyncs it, atomically replaces `<resolved Google Antigravity profile root>/design-arc-global.yaml`, and fsyncs the parent directory; `global off` writes off, while `global on` writes on only to clear the laptop ceiling and never force-enables project off. If the existing file is malformed or uses an unsupported schema, report that replacing it with the two-field v1 document will discard unreadable or unsupported state and require explicit confirmation for that repair before the atomic write.

Resolve graph assistance independently for a new review: an explicit one-review off override, project off, or global off each disables it; global on is only permission to resolve the project and can never force-enable project off. An explicit one-review on cannot override project off or global off. A saved project on remains disabled while global off is active and becomes eligible again when the global safety state is on.

For every new 0.3.0 review in an existing project whose preference has no `graph_assistance` field, resolve graph assistance to active by default.

For every new 0.3.0 review in a new project whose preference has no `graph_assistance` field, resolve graph assistance to active by default.

Default resolution and one-review overrides do not rewrite `.gemini/design-arc.yaml` or laptop-global safety state merely because a review resolved them. Write a project or global setting only when the user issues or clearly requests that scoped setting change.

At new-review start, assign one stable `review_id` and record `workflow_version: 0.3.0`; an already-active review retains its recorded workflow version and never changes behavior mid-review after an upgrade, downgrade, or setting change. Resolve the graph state once for that review and record it with the identity; later commands may disable use or manage its record, but do not rewrite the review's starting version.

At review start, report the graph active state and its provenance as current-request one-review override, saved project setting, laptop-global safety off, or 0.3.0 default; `graph explain` also reports the resolution chain, review ID, workflow version, graph path, and latest validation or fallback result. Keep graph provenance distinct from evidence-mode and approval-mode provenance.

#### Record, validation, and fallback

Store each record only at `.gemini/design-arc/reviews/<review_id>/graph.json`, require schema `design-arc.graph/v1`, and validate the current project ID and review ID before use; never read a graph from another project or review. Build the record only from authoritative facts established by the current workflow, keep edge provenance and support explicit, and replace relationships when their supporting facts change rather than treating stale links as current.

When graph assistance is active, construct or update the current review record as stable workflow facts become available. Resolve `scripts/validate-graph-record.py` relative to the directory containing this `SKILL.md`, never relative to the product workspace or repository root. Before relying on the graph, run `python3 <resolved Design Arc skill directory>/scripts/validate-graph-record.py GRAPH_PATH EXPECTED_PROJECT_ID EXPECTED_REVIEW_ID`; do not silently normalize or partially trust a rejected record.

Validate the complete graph before every use; if it is missing, invalid, corrupt, incomplete, contradictory, unsupported, unproven, or identity-mismatched, ignore it, report the reason, and continue the unchanged standard workflow without graph assistance. Graph failure is a downgrade in assistance, not a blocked gate; preserve the rejected file for explanation or confirmed rebuild/clear unless using it would cross a project boundary.

The graph advises correction planning only: it is not evidence, proof, approval, a source of requirements, or authority, and creating or using it adds no design approval gate. Source every graph node and relationship from the workflow record; never source the workflow record from an unsupported graph inference.

Current first-party requirements for the target platform override every conflicting graph relationship or graph-assisted suggestion.

Current accessibility requirements override every conflicting graph relationship or graph-assisted suggestion and cannot be waived by an exception edge.

Current inspected evidence and its recorded provenance override stale, inferred, unsupported, or contradictory graph relationships; never turn a relationship into an evidence claim.

#### Correction planning and unchanged inspection

Before a graph-assisted correction, trace render → screen/state → approved requirement → provenance → dependent states → regression checks, and omit any relationship that cannot complete this supported trace. Use the trace to identify the smallest compatible correction batch and the states most likely to regress; record which relationships informed the batch.

Use supported graph relationships only to batch compatible `repairable drift` across the proposal; never split the proposal-wide correction budget per node, screen, state, or branch. Direction decisions, authorization requirements, and runtime proof remain outside automatic correction.

After every graph-assisted correction round, perform the unchanged complete-proposal inspection, including previously matching and graph-unrelated screens and states that may have regressed. The graph may focus attention but never narrows the required conformance matrix or replaces render inspection.

Graph assistance preserves one initial visual proposal followed by at most three batched correction rounds for the entire proposal and never resets, extends, or bypasses that limit.

Graph assistance never bypasses Objective Confirmation, Direction Gate, Visual Proposal Gate, their approval-mode behavior, or the requirement that Fully automatic continues only on `meets direction`.

Graph relationships cannot establish runtime proof; carry implementation, staging, device, accessibility, performance, and production proof forward as unverified until current measured evidence establishes it.

#### Explain, rebuild, clear, and downgrade

`graph rebuild` reconstructs only the current review's graph from current authoritative workflow evidence, validates the replacement before use, and preserves the review ID, workflow version, project preference, and product files. Rebuild is not permission to redo research, change an approved direction, create requirements, or use another review's record; if validation fails, report fallback and keep the standard workflow active.

`graph clear` is destructive, requires explicit confirmation for the exact current-review graph path, deletes only that graph after confirmation, and then continues the standard workflow without graph assistance; it never clears preferences, product files, other reviews, or other projects. Before asking, state the exact path and that clearing does not turn the saved project or global setting off; without confirmation, leave the record unchanged.

Older workflow versions ignore unsupported graph records but preserve them during downgrade; graph controls, records, explanations, rebuilds, clears, and suggestions never authorize source implementation, dependency or provider changes, staging, deployment, release, or profile upgrade. Upgrade or downgrade handling must preserve project preferences, reminder blocks, active review identity/version records, graph files, and product files unless the user separately authorizes an exact destructive action.

### The six valid combinations

Evidence selection and approval behavior remain independent:

| Evidence | Approval | Gate behavior |
|---|---|---|
| Guidelines + Benchmarks | Guided | Direction Gate stops; Visual Proposal Gate stops |
| Guidelines + Benchmarks | Follow recommendation | Direction Gate continues with the marked recommendation; Visual Proposal Gate stops |
| Guidelines + Benchmarks | Fully automatic | Direction Gate continues; Visual Proposal Gate continues only on `meets direction` |
| Guidelines only | Guided | Direction Gate stops; Visual Proposal Gate stops |
| Guidelines only | Follow recommendation | Direction Gate continues with the marked recommendation; Visual Proposal Gate stops |
| Guidelines only | Fully automatic | Direction Gate continues; Visual Proposal Gate continues only on `meets direction` |

## Establish the objective

Make the user's desired outcome the criterion for every audit finding, evidence choice, direction, and render verdict.

- When the request is broad, offer two or three distinct plausible objectives and allow the user to enter their own.
- In Guided or Follow recommendation mode, restate a stated objective and ask the user to confirm or revise it.
- Fully automatic may skip the objective pause only when the current request states an explicit objective.
- If the objective is missing or materially ambiguous, stop and ask; never invent it.
- Do not inspect, research, or generate until the objective is confirmed or is explicit under Fully automatic.

Objective Confirmation is separate from the two design gates. “Follow your recommendation” changes the Direction Gate policy for one run; it does not confirm an objective or bypass Visual Proposal Gate. “Bypass both gates” is a one-run Fully automatic alias, but still requires an explicit current-request objective.

## Audit the real journey

Inspect the live or supplied product and its product contract against the established objective. Map the complete relevant journey, not an isolated screen:

- platform, orientation, viewport, region, entry point, and user goal;
- steps, screens, transitions, choices, and exits;
- loading, empty, error, success, cancellation, and recovery states;
- observed friction versus clearly labeled inference.

Do not redesign an imagined product. If current product evidence is unavailable, report the blocked audit and stop.

## Gather evidence

### Guidelines + Benchmarks

Confirm external benchmark access before research. Apply a light current first-party constraint check before looking for precedent so examples do not normalize a platform conflict.

Inspect complete, relevant real-product journeys and explain why each selected pattern is useful for the established objective. Library presence, metadata, popularity, or one screenshot never proves best-in-class quality. Record the product, journey, relevant states, current canonical link, inspection context, supported decision, limitations, and observed-versus-inferred status.

Mobbin is an optional external benchmark provider, not a bundled or official Design Arc integration. Access and authorization remain external and separate.

If benchmark access is missing, stop; never degrade silently. Offer either a one-run Guidelines only fallback that does not rewrite the saved preference, or a confirmed saved switch to Guidelines only. Do not continue until the user chooses, and do not describe a fallback result as benchmark-backed.

### Guidelines only

In Guidelines only mode, perform no benchmark lookup and make no benchmark-evidence claim. Look up current first-party guidance for every affected platform and link directly to the principles that constrain hierarchy, navigation, targets, labels, feedback, accessibility, errors, safe areas, and recovery.

Use Apple Human Interface Guidelines as first-party authority for Apple targets. For Android or web targets, current first-party platform rules override conflicting Apple-inspired judgment. Distinguish platform requirements from product-specific judgment.

## Recommend directions and apply the Direction Gate

Synthesize the audit and selected evidence into one recommended direction and meaningful alternatives. For each direction state:

- journey sequence and outcome logic;
- screens and states to add, remove, merge, or retain;
- key interaction changes and supporting evidence;
- material motion scope, retained existing or native behavior, proposed custom behavior, and unresolved motion evidence;
- benefits, risks, trade-offs, and unresolved questions.

At the Direction Gate, present one unmistakably marked recommendation plus meaningful alternatives and their trade-offs.

At the Direction Gate, include a motion summary that identifies the material motion scope, retained native or existing behavior, proposed custom behavior, and unresolved evidence.

For each direction, explain the motion's concrete interaction purpose and why it uses no more motion than that purpose requires.

For each direction, cite relevant inspected real-product evidence and current platform guidance, or state that either is unavailable.

For each direction, apply the required provenance label to every temporal claim and distinguish directly observed behavior from measured estimates.

For each direction, describe reduced-motion implications, motion-specific risks, and implementation complexity in the target stack.

For each direction, identify what remains unproven and the staging, device, or production evidence needed to prove it.

Headings or field names without these direction-specific explanations do not satisfy the Direction Gate.

- **Guided:** report the active settings and provenance, then stop for the user's direction choice.
- **Follow recommendation:** record that the active mode selected the marked recommendation, then continue.
- **Fully automatic:** record the same automatic selection, then continue.

An automatic selection is still visible and auditable; never hide the alternatives or their trade-offs.

## Validate and visualize the selected journey

Recheck the complete selected direction against current first-party guidance for every affected platform. Resolve conflicts before generation and report any product-specific judgment separately.

### Choose and manage the visualization surface

Confirm that the active host is Google Antigravity before recommending a visualization path. Never claim native image-generation capability in Google Antigravity. Google Antigravity may create HTML/CSS, SVG, specifications, and lightweight static journey boards. Do not build application logic, navigation logic, APIs, databases, production components, or throwaway prototype infrastructure merely to visualize the proposal. Include every material entry, transition, loading, empty, error, success, cancellation, and recovery state. Prefer one cohesive board first; generate an individual high-resolution screen only when closer inspection or a focused correction requires it.

Recommend Google Stitch early whenever the user wants polished screen mockups, visual exploration, editable layouts, or continued visual refinement. Stitch remains optional and separately authorized.

Recommend Stitch when any one genuine trigger occurs: polished screen mockups; visual exploration; editable layouts; continued visual refinement; a second meaningful visual direction; a change spanning three or more screens; precise layout, spacing, or styling iteration; user-directed canvas editing; likely continuation on another day; device variants; collaboration; or design export.

Do not withhold the Stitch recommendation when polished or editable mockups are requested. Otherwise, do not recommend Stitch merely because it is available, Mobbin supplied precedent, or one screen needs a bounded correction.

For the first relevant choice, use this exact prompt: “Antigravity can prepare a lightweight static journey board here. For polished, editable screen mockups, I recommend a Stitch-ready visual proposal. Which would you prefer?” A later recommendation is brief and appears only after another genuine trigger or materially larger scope.

When Stitch is recommended, present this numbered choice:

1. **Stitch** (recommended)
2. **Stay in Google Antigravity**
3. **Both**

Reply with `1`, `2`, or `3`. Both means create the Google Antigravity board and the Stitch visual workspace from the same approved journey. The active host remains the evidence, validation, and approval surface; inspect both outputs and reconcile material drift before assigning the visual verdict.

A Stitch recommendation is advisory: never transfer automatically, and continuing in Google Antigravity remains available. Treat `stay in Google Antigravity` as a choice for the current editing phase, not a permanent suppression. Never tell a Google Antigravity user to pass work to Codex unless the user explicitly requests a cross-platform handoff. If the user says not to recommend Stitch again for this review, suppress every further Stitch recommendation for that review.

Before using Stitch, prepare the complete evidence-grounded journey, requirements, and important-state inventory. When Stitch is selected, preserve the approved journey requirements, require separately authorized access, and compare retrieved or supplied changes before treating them as the current proposal. A Stitch share link, exported screens, Figma or HTML/CSS export, or `DESIGN.md` may support the return path. Use an exact configured Stitch MCP server or tool only when it is actually available and separately authorized; never imply that Design Arc bundles one. Retrieval means “inspect and show what changed,” not “silently approve or overwrite the direction.”

Stitch is a visualization tool, not an evidence authority. The active host must validate returned screens and apply the existing proposal-wide correction loop of up to three correction rounds. Apply the same complete-state conformance matrix, full reinspection, three-verdict standard, and Visual Proposal Gate regardless of renderer. `Visual Proposal Gate` is the renderer-neutral user-facing name for the existing `Stitch Gate` contract in 0.3.x records; do not create an additional gate or require preference migration.

### Bind the selected design to its production asset set

Treat a production asset set as the implementation-ready visual files, variants, and provenance needed to reproduce its design; it is not application logic and does not authorize implementation. The active AI coding platform must create a baseline design and a corresponding platform production asset set before design selection. For each asset set, keep a manifest with a stable asset ID, provenance, intended screen or component and state, required format and variants, source or export identifier, implementation reference, and desktop and mobile render-proof status. A required asset that cannot yet be generated or exported remains an explicit blocked manifest item, never an omitted requirement.

When Stitch is invoked, preserve its returned design and exported Stitch production asset set as a separate provenance-bound set; never overwrite either set with the other. Record the selected design as `platform`, `stitch`, or `hybrid` and bind it to the matching asset set before implementation handoff.

- A `platform` selection requires platform-generated assets and rejects every Stitch asset.
- A `stitch` selection requires exported Stitch assets and rejects platform-generated substitutes.
- `Both` creates comparable proposals, not permission to mix their assets; mixing is allowed only after the user explicitly approves a `hybrid` design and identifies which screens, elements, and assets come from each set.

After separate implementation authorization, require the built application to import, reference, and render every required asset from the selected asset set. Check the implementation source for the exact selected asset IDs, files, imports, and references, and reject unselected-set files, silent copies, lookalikes, regenerated substitutes, or placeholders. Block implementation completion when any required selected asset is missing, unused, broken, unavailable, substituted, or absent from the running application.

Keep controls, labels, navigation, state, status, focus behavior, and accessibility as semantic HTML or native UI; never flatten them into raster or vector artwork. Visual assets may decorate or illustrate those interfaces, but they must not replace programmatic names, roles, values, state changes, focus order, keyboard behavior, or assistive-technology behavior.

When a required asset is raster and the active AI coding platform lacks native image-generation capability, record it as blocked and stop before design completion or implementation handoff; HTML/CSS, SVG, placeholders, and invented substitutes do not satisfy it. Offer a separately authorized asset-generation or export path without claiming the active platform produced the raster.

Return `matches approved proposal` only after both source integration and rendered fidelity pass: verify exact selected-asset imports and references, then inspect the running application at desktop and mobile viewports for correct loading and visual fidelity. A source-only check, static proposal, build result, or one viewport is insufficient. Record mismatches and remain blocked until the selected assets appear correctly in the running application or the user explicitly changes the approved design; an implementation exception cannot silently redefine the selected proposal.

This asset-fidelity contract applies only after the existing design workflow and any separate implementation authorization. It does not let Design Arc authorize source changes, dependency installation, staging, deployment, or release, and it does not weaken Objective Confirmation, Direction Gate, Visual Proposal Gate, evidence integrity, platform guidance, accessibility, or the three-round visualization correction limit.

### Specify motion before visualization

Identify every material on-screen animation and screen-to-screen transition in the selected direction. If existing product motion or standard native behavior is sufficient, record that choice instead of inventing custom motion.

Apply the least-motion principle: use no more motion than the stated interaction purpose requires, and remove decorative motion without a justified purpose. Motion must communicate feedback, continuity, hierarchy, status, recovery, or another stated purpose.

#### Ground motion evidence

Use this motion-evidence precedence: existing product motion; native platform behavior and standard components; current first-party platform guidance; inspected relevant shipped-product motion; labeled Design Arc judgment. Prefer established product tokens and standard native components when they satisfy the interaction purpose. If sources conflict, the current target platform's first-party requirements govern that platform.

In Guidelines + Benchmarks mode, authorized shipped-product motion may be inspected as precedent. Static screens or sequences support only start/end state, changing element, journey location, and transition intent; they cannot support exact duration, easing, springs, velocity, interruption, or choreography. Never convert an unobserved benchmark animation into an exact motion claim.

For playable motion evidence, record source; product/journey; frame rate when known; observed duration/path/order; interruption/reversal; measurement method; confidence; and missing states. Frame-derived values are estimates.

Every temporal claim uses exactly one label: `directly observed`, `measured estimate`, `pattern-level inference`, `Design Arc judgment`, or `unverified`. The label describes the support for that claim, not the quality or authority of the source as a whole.

When necessary playable evidence is unavailable, report the limitation and offer an accessible live product, user recording, authorized Page Flows recording, native default, or labeled proposal requiring implementation validation. Never invent it.

In Guidelines only mode, perform no benchmark lookup, make no real-product motion claim, and report that no benchmark motion was inspected. Use current first-party guidance, standard native behavior, and labeled judgment without implying shipped-product precedent.

#### Write the material motion contracts

Every material motion contract includes: Motion ID; journey location; purpose; trigger; start/end state; spatial behavior; choreography; timing; easing/spring; interruption; reduced motion; evidence; provenance; implementation target; implementation source; proof status. Unsupported values are `unverified`.

Use one contract per motion or transition that affects continuity, feedback, hierarchy, status, recovery, spatial understanding, input, or accessibility. Record `none` only when absence is an inspected and deliberate value; use `unverified` when the value is unknown or unsupported. Reduced motion is a required alternative, not optional polish or `none`: preserve essential state and feedback without relying on nonessential displacement, scaling, parallax, or continuous motion.

`implementation target` records the runtime and UI technology, such as Web, React, SwiftUI, UIKit, or Compose; record component and state-change specificity separately when useful.

`timing` uses milliseconds or seconds for duration and delay, or records that a physical spring with explicit parameters governs timing.

`easing/spring` records cubic-bezier coordinates, a named platform curve, or physical spring parameters such as mass, stiffness, damping, and initial velocity.

`interruption` records whether motion can be interrupted or reversed, how cancellation resolves, and what happens on re-entry.

`provenance` uses exactly one of `directly observed`, `measured estimate`, `pattern-level inference`, `Design Arc judgment`, or `unverified` for each claim, cites the supporting source, and records the measurement or estimate basis when applicable.

`implementation source` names the existing product token, native or standard component, separately approved library, or custom implementation and records the authorizing owner; a proposal alone does not authorize it.

`proof status` distinguishes `specified`, `prototyped`, `staging verified`, `device verified`, and `production verified` as applicable; use only the highest status established by current evidence.

Motion+ is never required by or evidence for Design Arc, and it is never a Design Arc dependency. An authorized implementation owner may separately approve Motion+ as an optional implementation dependency and implementation source; that approval does not install it or make it Design Arc evidence or authority. Validate any resulting behavior independently.

After separate authorization from the implementation owner, Motion+ assistance may cover documentation and example search; reusable source retrieval; spring and easing assistance; saved-transition inspection; performance auditing; and design-system adaptation.

#### Preserve prototype, proof, and authority boundaries

Generated screens and design prototypes can illustrate states and transition intent but cannot prove timing, easing, springs, interruption, reduced-motion behavior, performance, or runtime implementation quality. If a prototype cannot express the required motion faithfully, return the start/end states and complete motion contract, label unsupported behavior `unverified`, and do not claim validation.

Only measured staging or target-device behavior can establish implementation proof. Record the tested runtime, viewport or device, accessibility setting, measurement method, result, and remaining gaps; a render, prototype, specification, source code, or library choice alone is not proof.

Design Arc may specify and critique motion, but it does not authorize application-code implementation, dependency installation, staging, deployment, or release. Passing the Visual Proposal Gate may route an approved contract to the authorized implementation owner; that owner retains stack, source, staging, and release authority.

For the default Google Antigravity route, prepare a lightweight static journey board with HTML/CSS, SVG, or specifications and avoid disposable application logic. When the user chooses Stitch, treat it as an external visualization service, not a bundled Design Arc integration; obtain whatever separate access and payload authorization the environment requires and use an existing project and design system when supplied. With either renderer, generate every material state required by the selected journey, including entry, transition, loading, empty, error, success, cancellation, and recovery. Record exact requested viewports, safe areas, assets, interaction states, renderer or board identifiers, and new screen identifiers.

Return decision-ready evidence in Google Antigravity: an inline journey map, embedded key renders, concise generator recommendations, exact verified render dimensions, identifiers, and evidence provenance. A board offers deeper exploration; it is not a substitute for the evidence in chat.

Before assigning a visual verdict, explicitly evaluate motion purpose and least-motion restraint, provenance labels and citations, reduced-motion behavior, alignment with every material motion contract, prototype limitations, and remaining runtime proof.

A `meets direction` verdict is valid only when the prototype aligns with those motion requirements within its capabilities and every limitation and remaining runtime proof item is documented; any unexplained gap yields `meets with corrections` or `does not meet`.

Fully automatic may continue on `meets direction` only after this motion evaluation is recorded; it cannot waive a missing or contradictory motion check.

Inspect the actual renders for journey coherence, hierarchy, navigation, targets, spacing, containment, safe areas, orientation, text size, accessibility, errors, and recovery. Give exactly one visual verdict: `meets direction`, `meets with corrections`, or `does not meet`.

### Repair visual drift before the Visual Proposal Gate

Use one initial visual proposal followed by at most three batched correction rounds for the entire proposal. The initial proposal is not a correction round, so the maximum is four rendered proposals.

Before assigning a visual verdict, create a conformance matrix for every material screen and state. Each row records the screen or state identifier; approved requirement and provenance; observed render evidence; classification; exact correction or next action; and inspected render identifier.

Classify every mismatch as `match`, `repairable drift`, `direction decision required`, or `runtime proof`. Correct `repairable drift` automatically without asking the user because it does not change the approved direction. Stop before correction when a direction decision or new external authorization is required. Carry `runtime proof` forward as unverified implementation evidence; do not retry the renderer or claim the prototype proves it.

A correction note, provider status, or command success is not proof of correction; only inspection of the newly generated render can change a mismatch to `match`. After every correction round, inspect the complete resulting proposal again, including previously matching requirements that may have regressed.

Run this bounded sequence:

```text
initial complete proposal
→ conformance inspection
→ batched repairable-drift correction
→ complete reinspection
→ repeat for at most three correction rounds
→ final verdict
→ existing Visual Proposal Gate policy
```

Each correction request identifies the source render and affected screen/state IDs; states the observed mismatch and exact approved requirement; changes only `repairable drift`; preserves already matching requirements and the approved direction; requests a complete enough result to re-inspect affected and potentially regressed states; and records the new render or screen identifiers returned by the active renderer. Add newly introduced drift to the next batched round.

Stop early only when two consecutive corrected proposals show no improvement, two consecutive corrected proposals oscillate by fixing one requirement while breaking another, access becomes unavailable, the next correction changes direction, or new authorization is required. After the third unsuccessful correction round, stop and assign `meets with corrections` or `does not meet` from the remaining mismatch scope. Use `meets with corrections` only when unresolved bounded mismatches remain and the approved direction is still recognizable. Use `does not meet` when the proposal materially contradicts or fails to represent the approved direction.

Assign `meets direction` only after the most recent complete proposal is inspected and every renderer-expressible requirement matches. Guided and Follow recommendation perform the repair loop before stopping at the Visual Proposal Gate. After an unresolved verdict in Guided or Follow recommendation, offer the user choices to revise the direction, accept a clearly labeled product exception where allowed, or stop; an exception cannot change the verdict to `meets direction` or waive a current first-party platform or accessibility requirement. Fully automatic performs the same repair loop and continues past the Visual Proposal Gate only on `meets direction`.

Record the initial proposal identifiers; each conformance matrix; correction round number; batched correction request and provenance; fixed, remaining, and newly introduced mismatches; stop reason; final visual verdict; and remaining runtime proof.

## Apply the Visual Proposal Gate and hand off

- **Guided and Follow recommendation:** stop after the verdict and request approval.
- **Fully automatic:** Fully automatic continues only when the visual verdict is `meets direction`; `meets with corrections` and `does not meet` both stop.

Passing Visual Proposal Gate authorizes only a coordinated handoff of the validated design proposal. Design approval never authorizes source implementation, staging, live deployment, release, destructive changes, provider changes, or work outside the authorized integration lane. Treat later refinements as amendments to one canonical handoff rather than duplicate tasks.

## Required run record

Report these fields in the Google Antigravity conversation:

- **Setup:** active evidence mode, active approval mode, provenance of each, saved values, and one-run overrides.
- **Objective:** confirmed outcome or explicit Fully automatic objective and evaluation criterion.
- **Current journey:** surface, platform, entry, steps, material states, friction, and evidence status.
- **Evidence:** source type, current links, inspected scope, what each source supports, and limitations.
- **Directions:** marked recommendation, alternatives, exact journey changes, and trade-offs.
- **Gates:** Objective Confirmation, Direction Gate, and Visual Proposal Gate status and reason.
- **Proposal:** journey map, embedded key renders, viewports, identifiers, and material states.
- **Motion:** material animations and transitions, motion scope, evidence and provenance, complete contracts, reduced motion, implementation source, proof, and remaining uncertainty.
- **Validation:** visual verdict, corrections, blocked proof, and remaining device or implementation checks.
- **Asset fidelity:** platform and Stitch asset manifests when applicable, selected design and bound asset set, explicit hybrid approval if any, blocked assets, source integration evidence, desktop and mobile rendered evidence, and remaining mismatches.
- **Authority:** design-only status and next authorized owner.

## Evidence and authorization integrity

Do not claim product inspection, first-party guidance, benchmark evidence, or new generated output without current evidence for that exact claim. Do not claim exact render dimensions from metadata alone. Do not claim accessibility, safe-area, browser, native, or device compliance from appearance alone; identify the measured implementation proof still required.

No approval mode waives current-source evidence, external authorization, platform precedence, complete-state coverage, render critique, or ownership. If any required source or service is unavailable, report the exact blocked gate and the partial evidence that remains valid.

Relevant run records include motion scope, evidence, provenance, contracts, reduced motion, implementation source, proof, and remaining uncertainty.

Fully automatic mode never bypasses motion evidence integrity.

## Common mistakes

- Treating the two choices as one combined “mode” instead of resolving evidence and approval independently.
- Inspecting the product or researching before setup and Objective Confirmation.
- Rewriting a saved preference because of a one-run override.
- Silently importing or merging legacy preferences.
- Falling back from Guidelines + Benchmarks without the user's choice.
- Calling a popular screenshot “best in class” without inspecting its journey.
- Inferring exact motion timing, easing, springs, or choreography from a screenshot or static screen sequence.
- Reporting a frame-derived value as exact or omitting the temporal-claim label.
- Claiming shipped-product motion precedent in Guidelines only mode.
- Treating Motion or Motion+ as Design Arc evidence, authority, dependency, or permission to install; an authorized implementation owner's separate optional dependency choice does not change that boundary.
- Treating a Stitch prototype as staging or device implementation proof.
- Inventing custom motion when existing product or standard native behavior already serves the purpose.
- Looking up benchmarks or implying benchmark support in Guidelines only mode.
- Inventing a missing objective under Fully automatic.
- Hiding alternatives because Follow recommendation is active.
- Treating `meets with corrections` as permission to pass Visual Proposal Gate.
- Omitting non-happy states from the generated journey.
- Treating a design approval as implementation or release authorization.
