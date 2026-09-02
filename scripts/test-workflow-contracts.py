#!/usr/bin/env python3
"""Mutation tests for the Design Arc instruction-contract checker.

These tests prove that the deterministic checker rejects missing or reversed
workflow clauses. They do not simulate an agent; scenario evidence covers that
separate question.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKER = REPO_ROOT / "scripts/check-workflow-contracts.py"
SKILL = REPO_ROOT / "plugins/design-arc/skills/design-arc/SKILL.md"


MUTATIONS = {
    "setup before inspection": (
        "Resolve setup before product inspection, external research, or generation. Then establish the user's objective before any of those activities.",
        "Inspect the product before resolving setup, then infer the objective.",
    ),
    "setup command": ("`$design-arc setup`", "`$design-arc configure`"),
    "home command": ("`$design-arc home`", "`$design-arc dashboard`"),
    "upgrade command": ("`$design-arc upgrade`", "`$design-arc reinstall-every-project`"),
    "benchmark command": (
        "`$design-arc evidence benchmarks`",
        "`$design-arc evidence examples`",
    ),
    "guidelines command": (
        "`$design-arc evidence guidelines`",
        "`$design-arc evidence standards`",
    ),
    "mode report command": ("`$design-arc mode`", "`$design-arc status`"),
    "guided command": (
        "`$design-arc mode guided`",
        "`$design-arc mode manual`",
    ),
    "follow command": (
        "`$design-arc mode follow-recommendation`",
        "`$design-arc mode recommended`",
    ),
    "automatic command": (
        "`$design-arc mode fully-automatic`",
        "`$design-arc mode automatic`",
    ),
    "override precedence": (
        "1. Explicit one-run override in the current request; do not save it unless asked.",
        "1. Saved preference; ignore a current-request override.",
    ),
    "saved preference precedence": (
        "2. Saved `.codex/design-arc.yaml` value.",
        "2. A global default outside the project.",
    ),
    "confirmed import precedence": (
        "3. Confirmed legacy import, only when the new file is absent.",
        "3. Silent legacy import, even when the new file exists.",
    ),
    "first-use precedence": (
        "4. First-use selection for every choice still missing.",
        "4. Infer every choice still missing.",
    ),
    "mode provenance": (
        "Always report the active evidence mode and approval mode, and the provenance of each independently.",
        "Report the active modes without their provenance.",
    ),
    "separate first-use turns": (
        "Collect first-use evidence and approval choices in two separate user turns. Never present both choice lists in the same message.",
        "Present evidence and approval choices together in one message.",
    ),
    "Mobbin recommendation": (
        "**Guidelines + Mobbin benchmarks — recommended.**",
        "**Guidelines only — recommended here.**",
    ),
    "Mobbin Pro prerequisite": (
        "Ensure you have an active Mobbin Pro account before choosing this option",
        "Mobbin access is assumed and needs no account.",
    ),
    "numeric evidence reply": (
        "Ask the user to reply with `1` or `2`.",
        "Ask the user to type the complete evidence-mode name.",
    ),
    "numeric approval reply": (
        "Ask the user to reply with `1`, `2`, or `3`.",
        "Ask the user to provide both setup choices together.",
    ),
    "benchmarks guided combination": (
        "| Guidelines + Benchmarks | Guided | Direction Gate stops; Visual Proposal Gate stops |",
        "| Guidelines + Benchmarks | Guided | Both gates continue |",
    ),
    "benchmarks follow combination": (
        "| Guidelines + Benchmarks | Follow recommendation | Direction Gate continues with the marked recommendation; Visual Proposal Gate stops |",
        "| Guidelines + Benchmarks | Follow recommendation | Both gates continue |",
    ),
    "benchmarks automatic combination": (
        "| Guidelines + Benchmarks | Fully automatic | Direction Gate continues; Visual Proposal Gate continues only on `meets direction` |",
        "| Guidelines + Benchmarks | Fully automatic | Visual Proposal Gate continues on any verdict |",
    ),
    "guidelines guided combination": (
        "| Guidelines only | Guided | Direction Gate stops; Visual Proposal Gate stops |",
        "| Guidelines only | Guided | Both gates continue |",
    ),
    "guidelines follow combination": (
        "| Guidelines only | Follow recommendation | Direction Gate continues with the marked recommendation; Visual Proposal Gate stops |",
        "| Guidelines only | Follow recommendation | Both gates continue |",
    ),
    "guidelines automatic combination": (
        "| Guidelines only | Fully automatic | Direction Gate continues; Visual Proposal Gate continues only on `meets direction` |",
        "| Guidelines only | Fully automatic | Visual Proposal Gate continues on any verdict |",
    ),
    "benchmark journey quality": (
        "Inspect complete, relevant real-product journeys and explain why each selected pattern is useful for the established objective.",
        "Treat a library listing as sufficient benchmark proof.",
    ),
    "benchmark quality exclusions": (
        "Library presence, metadata, popularity, or one screenshot never proves best-in-class quality.",
        "Popularity or one screenshot proves best-in-class quality.",
    ),
    "guidelines no benchmark lookup": (
        "In Guidelines only mode, perform no benchmark lookup and make no benchmark-evidence claim.",
        "In Guidelines only mode, quietly use benchmark evidence when convenient.",
    ),
    "missing access stop": (
        "If connection is declined or verification fails, stop; never degrade silently.",
        "If benchmark access is missing, silently continue with guidelines.",
    ),
    "connect Mobbin now": (
        "`1. Connect Mobbin now — recommended`, `2. Continue this review with Guidelines only`, `3. Cancel the review`.",
        "Continue with Guidelines only without offering a Mobbin connection.",
    ),
    "one-run fallback": (
        "Only then offer the one-run Guidelines only fallback, which does not rewrite the saved preference.",
        "Switch the saved preference to Guidelines only without asking.",
    ),
    "fb ux import": (
        "`.codex/fb-ux.yaml` maps to `evidence_mode: benchmarks`, `benchmark_provider: mobbin`, and its preserved approval mode.",
        "`.codex/fb-ux.yaml` maps to Guidelines only and drops its approval mode.",
    ),
    "apple skill import": (
        "`.codex/apple-guidelines-stitch.yaml` maps to `evidence_mode: guidelines`, omits `benchmark_provider`, and preserves its approval mode.",
        "`.codex/apple-guidelines-stitch.yaml` maps to Guidelines + Benchmarks and adds a provider.",
    ),
    "confirm import": (
        "Show the proposed mapping and ask once before importing it.",
        "Import the mapping without showing or confirming it.",
    ),
    "dual legacy conflict": (
        "If both legacy files exist, present both mappings and require the user to choose one or start fresh.",
        "If both legacy files exist, merge them automatically.",
    ),
    "legacy preservation": (
        "Never silently merge, rewrite, or delete either legacy preference file.",
        "Merge and delete legacy preference files after import.",
    ),
    "guided objective confirmation": (
        "In Guided or Follow recommendation mode, restate a stated objective and ask the user to confirm or revise it.",
        "In Guided or Follow recommendation mode, infer and accept the objective.",
    ),
    "automatic explicit objective": (
        "Fully automatic may skip the objective pause only when the current request states an explicit objective.",
        "Fully automatic may invent a missing objective.",
    ),
    "missing objective stop": (
        "If the objective is missing or materially ambiguous, stop and ask; never invent it.",
        "If the objective is missing or materially ambiguous, infer it and continue.",
    ),
    "direction recommendation": (
        "At the Direction Gate, present one unmistakably marked recommendation plus meaningful alternatives and their trade-offs.",
        "At the Direction Gate, present only one direction without trade-offs.",
    ),
    "automatic stitch verdict": (
        "Fully automatic continues only when the visual verdict is `meets direction`; `meets with corrections` and `does not meet` both stop.",
        "Fully automatic continues when the visual verdict is `meets with corrections`.",
    ),
    "platform precedence": (
        "For Android or web targets, current first-party platform rules override conflicting Apple-inspired judgment.",
        "For Android or web targets, Apple-inspired judgment overrides first-party rules.",
    ),
    "source evidence integrity": (
        "Do not claim product inspection, first-party guidance, benchmark evidence, or new generated output without current evidence for that exact claim.",
        "Claim inspection and evidence based on prior metadata.",
    ),
    "repair round maximum": (
        "The initial proposal is not a correction round, so the maximum is four rendered proposals.",
        "The initial proposal is a correction round, so unlimited rendered proposals are allowed.",
    ),
    "proposal-wide batching": (
        "Each correction request identifies the source render and affected screen/state IDs; states the observed mismatch and exact approved requirement; changes only `repairable drift`; preserves already matching requirements and the approved direction; requests a complete enough result to re-inspect affected and potentially regressed states; and records the new render or screen identifiers returned by the active renderer.",
        "Each correction request may target one mismatch at a time, need not state the approved requirement, may change matching requirements, and may rely on a summary instead of enough output to inspect regressions.",
    ),
    "repair before user involvement": (
        "Correct `repairable drift` automatically without asking the user because it does not change the approved direction.",
        "Ask the user to approve every `repairable drift` correction before continuing.",
    ),
    "conformance matrix completeness": (
        "Each row records the screen or state identifier; approved requirement and provenance; observed render evidence; classification; exact correction or next action; and inspected render identifier.",
        "Each row records only the screen identifier and broad visual impression.",
    ),
    "correction proof requires render": (
        "A correction note, provider status, or command success is not proof of correction; only inspection of the newly generated render can change a mismatch to `match`.",
        "A correction note, provider status, or command success is proof of correction without inspecting a render.",
    ),
    "complete reinspection": (
        "After every correction round, inspect the complete resulting proposal again, including previously matching requirements that may have regressed.",
        "After every correction round, inspect only the corrected requirements.",
    ),
    "direction decision stop": (
        "Stop before correction when a direction decision or new external authorization is required.",
        "Automatically correct mismatches that require a direction decision or new external authorization.",
    ),
    "runtime proof boundary": (
        "Carry `runtime proof` forward as unverified implementation evidence; do not retry the renderer or claim the prototype proves it.",
        "Retry Stitch until `runtime proof` is resolved and claim the prototype proves it.",
    ),
    "two-round early-stop evidence": (
        "Stop early only when two consecutive corrected proposals show no improvement, two consecutive corrected proposals oscillate by fixing one requirement while breaking another, access becomes unavailable, the next correction changes direction, or new authorization is required.",
        "Stop after one corrected proposal that appears unchanged.",
    ),
    "third-round exhaustion verdict": (
        "After the third unsuccessful correction round, stop and assign `meets with corrections` or `does not meet` from the remaining mismatch scope. Use `meets with corrections` only when unresolved bounded mismatches remain and the approved direction is still recognizable. Use `does not meet` when the proposal materially contradicts or fails to represent the approved direction.",
        "After the third unsuccessful correction round, keep retrying until the proposal matches and treat any remaining mismatch as `meets direction`.",
    ),
    "no unexplained meets-direction verdict": (
        "Assign `meets direction` only after the most recent complete proposal is inspected and every renderer-expressible requirement matches.",
        "Assign `meets direction` before complete inspection when mismatches remain unexplained.",
    ),
    "repair run record": (
        "Record the initial proposal identifiers; each conformance matrix; correction round number; batched correction request and provenance; fixed, remaining, and newly introduced mismatches; stop reason; final visual verdict; and remaining runtime proof.",
        "Record only the final visual verdict and omit repair evidence.",
    ),
    "guided and follow repair timing": (
        "Guided and Follow recommendation perform the repair loop before stopping at the Visual Proposal Gate. After an unresolved verdict in Guided or Follow recommendation, offer the user choices to revise the direction, accept a clearly labeled product exception where allowed, or stop; an exception cannot change the verdict to `meets direction` or waive a current first-party platform or accessibility requirement.",
        "Guided and Follow recommendation stop at the Visual Proposal Gate before the repair loop and silently treat unresolved drift as approved.",
    ),
    "fully automatic repair verdict": (
        "Fully automatic performs the same repair loop and continues past the Visual Proposal Gate only on `meets direction`.",
        "Fully automatic bypasses the repair loop and continues past the Visual Proposal Gate on any verdict.",
    ),
    "motion case 01 evidence precedence": (
        "Use this motion-evidence precedence: existing product motion; native platform behavior and standard components; current first-party platform guidance; inspected relevant shipped-product motion; labeled Design Arc judgment.",
        "Use labeled Design Arc judgment before checking product, platform, or shipped-product motion.",
    ),
    "motion case 02 benchmark and static limits": (
        "Static screens or sequences support only start/end state, changing element, journey location, and transition intent; they cannot support exact duration, easing, springs, velocity, interruption, or choreography.",
        "Static screens support exact duration, easing, springs, velocity, interruption, and choreography.",
    ),
    "motion case 02 benchmark authorization": (
        "In Guidelines + Benchmarks mode, authorized shipped-product motion may be inspected as precedent.",
        "In Guidelines + Benchmarks mode, inspect shipped-product motion without authorization.",
    ),
    "motion case 03 playable evidence record": (
        "For playable motion evidence, record source; product/journey; frame rate when known; observed duration/path/order; interruption/reversal; measurement method; confidence; and missing states. Frame-derived values are estimates.",
        "For playable motion evidence, record only the source and copy frame-derived values as exact.",
    ),
    "motion case 04 temporal claim labels": (
        "Every temporal claim uses exactly one label: `directly observed`, `measured estimate`, `pattern-level inference`, `Design Arc judgment`, or `unverified`.",
        "Temporal claims need no evidence label.",
    ),
    "motion case 05 unavailable playable evidence": (
        "When necessary playable evidence is unavailable, report the limitation and offer an accessible live product, user recording, authorized Page Flows recording, native default, or labeled proposal requiring implementation validation. Never invent it.",
        "When playable evidence is unavailable, invent a plausible animation from a static screen.",
    ),
    "motion case 06 Guidelines isolation": (
        "In Guidelines only mode, perform no benchmark lookup, make no real-product motion claim, and report that no benchmark motion was inspected.",
        "In Guidelines only mode, imply real-product motion was inspected without a benchmark lookup.",
    ),
    "motion case 07 complete contract fields": (
        "Every material motion contract includes: Motion ID; journey location; purpose; trigger; start/end state; spatial behavior; choreography; timing; easing/spring; interruption; reduced motion; evidence; provenance; implementation target; implementation source; proof status. Unsupported values are `unverified`.",
        "Every material motion contract includes only Motion ID, purpose, and timing; omit unsupported fields.",
    ),
    "motion case 07 target semantics": (
        "`implementation target` records the runtime and UI technology, such as Web, React, SwiftUI, UIKit, or Compose; record component and state-change specificity separately when useful.",
        "`implementation target` records only a vague screen or component name and omits the runtime and UI technology.",
    ),
    "motion case 07 timing semantics": (
        "`timing` uses milliseconds or seconds for duration and delay, or records that a physical spring with explicit parameters governs timing.",
        "`timing` uses subjective values such as fast or smooth without units or spring parameters.",
    ),
    "motion case 07 easing semantics": (
        "`easing/spring` records cubic-bezier coordinates, a named platform curve, or physical spring parameters such as mass, stiffness, damping, and initial velocity.",
        "`easing/spring` records only a vague adjective and no reproducible curve or spring parameters.",
    ),
    "motion case 07 interruption semantics": (
        "`interruption` records whether motion can be interrupted or reversed, how cancellation resolves, and what happens on re-entry.",
        "`interruption` records only yes or no and omits reversal, cancellation, and re-entry behavior.",
    ),
    "motion case 07 provenance semantics": (
        "`provenance` uses exactly one of `directly observed`, `measured estimate`, `pattern-level inference`, `Design Arc judgment`, or `unverified` for each claim, cites the supporting source, and records the measurement or estimate basis when applicable.",
        "`provenance` accepts unlabeled claims without citations or an estimate basis.",
    ),
    "motion case 07 source authorization semantics": (
        "`implementation source` names the existing product token, native or standard component, separately approved library, or custom implementation and records the authorizing owner; a proposal alone does not authorize it.",
        "`implementation source` lists an unapproved library and treats the proposal as installation authorization.",
    ),
    "motion case 07 proof-status semantics": (
        "`proof status` distinguishes `specified`, `prototyped`, `staging verified`, `device verified`, and `production verified` as applicable; use only the highest status established by current evidence.",
        "`proof status` uses complete for every design and promotes it without runtime evidence.",
    ),
    "motion case 08 Design Arc dependency boundary": (
        "Motion+ is never required by or evidence for Design Arc, and it is never a Design Arc dependency.",
        "Motion+ is required evidence for Design Arc and a Design Arc dependency.",
    ),
    "motion case 08 implementation owner boundary": (
        "An authorized implementation owner may separately approve Motion+ as an optional implementation dependency and implementation source; that approval does not install it or make it Design Arc evidence or authority.",
        "Design Arc automatically installs Motion+ as a required implementation dependency and treats it as motion evidence.",
    ),
    "motion case 08 authorized assistance scope": (
        "After separate authorization from the implementation owner, Motion+ assistance may cover documentation and example search; reusable source retrieval; spring and easing assistance; saved-transition inspection; performance auditing; and design-system adaptation.",
        "Motion+ may autonomously install itself and redesign the product without implementation-owner authorization.",
    ),
    "motion case 09 direction summary": (
        "At the Direction Gate, include a motion summary that identifies the material motion scope, retained native or existing behavior, proposed custom behavior, and unresolved evidence.",
        "At the Direction Gate, omit the motion scope and unresolved evidence.",
    ),
    "motion case 09 least-motion principle": (
        "Apply the least-motion principle: use no more motion than the stated interaction purpose requires, and remove decorative motion without a justified purpose.",
        "Add decorative motion even when it serves no interaction purpose.",
    ),
    "motion case 09 direction purpose semantics": (
        "For each direction, explain the motion's concrete interaction purpose and why it uses no more motion than that purpose requires.",
        "For each direction, list a motion-purpose heading without explaining the interaction purpose or restraint.",
    ),
    "motion case 09 direction evidence semantics": (
        "For each direction, cite relevant inspected real-product evidence and current platform guidance, or state that either is unavailable.",
        "For each direction, claim evidence and guidance support without citations or availability status.",
    ),
    "motion case 09 direction provenance semantics": (
        "For each direction, apply the required provenance label to every temporal claim and distinguish directly observed behavior from measured estimates.",
        "For each direction, combine observations and estimates under an unlabeled evidence heading.",
    ),
    "motion case 09 direction accessibility and delivery semantics": (
        "For each direction, describe reduced-motion implications, motion-specific risks, and implementation complexity in the target stack.",
        "For each direction, omit reduced-motion implications, motion-specific risks, and target-stack complexity.",
    ),
    "motion case 09 direction proof semantics": (
        "For each direction, identify what remains unproven and the staging, device, or production evidence needed to prove it.",
        "For each direction, claim completion without identifying remaining proof.",
    ),
    "motion case 09 headings are insufficient": (
        "Headings or field names without these direction-specific explanations do not satisfy the Direction Gate.",
        "Direction Gate is satisfied by empty headings or field names alone.",
    ),
    "motion case 10 prototype proof boundary": (
        "Generated screens and design prototypes can illustrate states and transition intent but cannot prove timing, easing, springs, interruption, reduced-motion behavior, performance, or runtime implementation quality.",
        "Treat a Stitch prototype as proof of timing, reduced-motion behavior, performance, and runtime implementation quality.",
    ),
    "motion case 10 staging and device proof": (
        "Only measured staging or target-device behavior can establish implementation proof.",
        "A static design specification establishes implementation proof without staging or device measurement.",
    ),
    "motion case 10 implementation authority": (
        "Design Arc may specify and critique motion, but it does not authorize application-code implementation, dependency installation, staging, deployment, or release.",
        "A Design Arc motion contract authorizes implementation, dependency installation, staging, deployment, and release.",
    ),
    "motion case 10 verdict evaluation": (
        "Before assigning a visual verdict, explicitly evaluate motion purpose and least-motion restraint, provenance labels and citations, reduced-motion behavior, alignment with every material motion contract, prototype limitations, and remaining runtime proof.",
        "Assign the visual verdict from visual polish without evaluating motion provenance, reduced motion, contract alignment, or remaining proof.",
    ),
    "motion case 10 meets-direction semantics": (
        "A `meets direction` verdict is valid only when the prototype aligns with those motion requirements within its capabilities and every limitation and remaining runtime proof item is documented; any unexplained gap yields `meets with corrections` or `does not meet`.",
        "Use `meets direction` despite unexplained motion gaps and undocumented runtime proof.",
    ),
    "motion case 10 automatic evaluation gate": (
        "Fully automatic may continue on `meets direction` only after this motion evaluation is recorded; it cannot waive a missing or contradictory motion check.",
        "Fully automatic may continue without recording the motion evaluation and may waive contradictory checks.",
    ),
    "motion case 11 run record": (
        "Relevant run records include motion scope, evidence, provenance, contracts, reduced motion, implementation source, proof, and remaining uncertainty.",
        "Relevant run records omit provenance, implementation source, proof, and uncertainty.",
    ),
    "motion case 12 automatic integrity": (
        "Fully automatic mode never bypasses motion evidence integrity.",
        "Fully automatic mode may bypass motion evidence integrity.",
    ),
    "implementation boundary": (
        "Design approval never authorizes source implementation, staging, live deployment, release, destructive changes, provider changes, or work outside the authorized integration lane.",
        "Design approval authorizes implementation and live deployment.",
    ),
    "renderer default avoids disposable app logic": (
        "Confirm that the active host is Codex before recommending a visualization path. Create static screen images and complete journey boards directly in Codex by default.",
        "Build a coded interactive application prototype by default.",
    ),
    "Stitch remains optional": (
        "Google Stitch is valuable for canvas-based editing, multiple visual alternatives, and sustained visual refinement. Direct Codex generation is the quickest static-board route. Stitch remains optional and separately authorized.",
        "Google Stitch is mandatory for every Design Arc review.",
    ),
    "upfront renderer timing": (
        "Immediately after the Direction Gate resolves and before either renderer starts, present the visualization choice once.",
        "Wait until the Codex render is inadequate before mentioning Stitch.",
    ),
    "three-way visualization choice": (
        "1. **Both Codex and Stitch — recommended**",
        "Offer only Stitch or Codex; do not offer both.",
    ),
    "Both concurrent initial renders": (
        "When the user selects `Both`, start the AI coding platform visualization and the Stitch visualization concurrently from the same approved specification.",
        "When the user selects `Both`, render in Codex first and start Stitch only after Codex correction finishes.",
    ),
    "Both initial-render barrier": (
        "Do not begin any correction round until both initial renders have finished successfully.",
        "Begin correcting the first renderer as soon as it finishes, even while the other initial render is pending.",
    ),
    "Both independent inspection": (
        "After both initial renders finish, inspect each renderer independently against the same approved specification and record a separate conformance matrix and renderer-specific verdict before cross-comparing them.",
        "Use the preferred renderer as the standard for judging the other renderer.",
    ),
    "Both shared correction budget": (
        "Treat `Both` as one paired proposal with one shared correction-round counter: at most three proposal-wide correction rounds total, not three rounds per renderer.",
        "Give Codex and Stitch three independent correction rounds each.",
    ),
    "Both explicit correction scope": (
        "After the independent comparison, record the active correction scope as `platform`, `stitch`, or `both` from the user's explicit choice; selecting `Both` for initial generation does not select both renderers for correction.",
        "Selecting `Both` for initial generation automatically selects both renderers for every correction.",
    ),
    "Both single-renderer correction isolation": (
        "Correct only the renderer or renderers in the active correction scope, and preserve every unselected render and its independent inspection unchanged as comparison evidence.",
        "Correct both renderers whenever either has drift, even if the user selected only one for refinement.",
    ),
    "Both correction concurrency is conditional": (
        "Run corrections concurrently only when the active correction scope is `both`; when it is `platform` or `stitch`, run only that renderer and do not wait for or modify the other.",
        "Always run both corrections concurrently after an initial Both comparison.",
    ),
    "Both selected correction barrier": (
        "For a `both` correction round, send renderer-specific correction batches concurrently, wait for both requested correction renders to finish, then reinspect each renderer independently before comparing the pair.",
        "Correct and approve whichever selected renderer finishes each correction first.",
    ),
    "Both failure fallback": (
        "If either initial renderer fails or becomes unavailable, stop the `Both` path and report the incomplete comparison; do not correct the completed renderer unless the user explicitly selects a single-renderer fallback.",
        "If one initial renderer fails, silently continue correcting and approving the completed renderer.",
    ),
    "advisory transfer": (
        "A renderer recommendation is advisory: never transfer automatically, and every listed route remains available.",
        "Automatically transfer the proposal to Stitch after a trigger.",
    ),
    "renderer choice is recorded once": (
        "Record the selected initial renderer scope once; do not re-ask unless the user explicitly changes it or a selected renderer becomes unavailable.",
        "Re-ask the renderer choice before every correction round.",
    ),
    "renderer choice can change explicitly": (
        "unless the user explicitly changes it or a selected renderer becomes unavailable.",
        "even when the user explicitly changes it or a selected renderer becomes unavailable.",
    ),
    "renderer-neutral validation": (
        "Stitch is a visualization tool, not an evidence authority. The active host must validate returned screens and apply the existing proposal-wide correction loop of up to three correction rounds.",
        "Use a lighter validation standard for Codex-generated screens.",
    ),
    "asset fidelity 01 platform baseline": (
        "The active AI coding platform must create a baseline design and a corresponding platform production asset set before design selection.",
        "The active AI coding platform may skip its baseline design and production asset set.",
    ),
    "asset fidelity 02 Stitch set preservation": (
        "When Stitch is invoked, preserve its returned design and exported Stitch production asset set as a separate provenance-bound set; never overwrite either set with the other.",
        "When Stitch is invoked, replace the platform design and assets with the Stitch result.",
    ),
    "asset fidelity 03 selected-design binding": (
        "Record the selected design as `platform`, `stitch`, or `hybrid` and bind it to the matching asset set before implementation handoff.",
        "Allow implementation handoff without recording which design and asset set were selected.",
    ),
    "asset fidelity 04 implementation integration": (
        "After separate implementation authorization, require the built application to import, reference, and render every required asset from the selected asset set.",
        "After implementation authorization, allow the built application to omit selected assets.",
    ),
    "asset fidelity 05 platform-selection isolation": (
        "A `platform` selection requires platform-generated assets and rejects every Stitch asset.",
        "A `platform` selection may use Stitch assets as silent substitutes.",
    ),
    "asset fidelity 06 Stitch-selection isolation": (
        "A `stitch` selection requires exported Stitch assets and rejects platform-generated substitutes.",
        "A `stitch` selection may use platform-generated substitutes.",
    ),
    "asset fidelity 07 explicit hybrid approval": (
        "`Both` creates comparable proposals, not permission to mix their assets; mixing is allowed only after the user explicitly approves a `hybrid` design and identifies which screens, elements, and assets come from each set.",
        "`Both` silently permits any mixture of platform and Stitch assets.",
    ),
    "asset fidelity 08 blocking failures": (
        "Block implementation completion when any required selected asset is missing, unused, broken, unavailable, substituted, or absent from the running application.",
        "Allow implementation completion when required selected assets are missing or not rendered.",
    ),
    "asset fidelity 09 semantic UI": (
        "Keep controls, labels, navigation, state, status, focus behavior, and accessibility as semantic HTML or native UI; never flatten them into raster or vector artwork.",
        "Flatten controls, labels, navigation, state, status, focus behavior, and accessibility into artwork.",
    ),
    "asset fidelity 10 raster capability block": (
        "When a required asset is raster and the active AI coding platform lacks native image-generation capability, record it as blocked and stop before design completion or implementation handoff; HTML/CSS, SVG, placeholders, and invented substitutes do not satisfy it.",
        "When native image generation is unavailable, treat HTML/CSS or SVG as a required raster asset.",
    ),
    "asset fidelity 11 source and rendered proof": (
        "Return `matches approved proposal` only after both source integration and rendered fidelity pass: verify exact selected-asset imports and references, then inspect the running application at desktop and mobile viewports for correct loading and visual fidelity.",
        "Return `matches approved proposal` after source inspection without desktop and mobile runtime evidence.",
    ),
    "saved project resolution": (
        "Call `list_projects` before any home lookup or creation and resolve the current saved project's `projectId` and saved-project name; use the workspace-folder name only when the saved-project name is unavailable.",
        "Infer a project from the task title without calling `list_projects`.",
    ),
    "canonical project title": (
        "The canonical title is `Design Arc — <Project Name>`.",
        "The canonical title is `Design Arc Home`.",
    ),
    "home setup confirmation": (
        "Home creation must be part of the setup proposal and must be explicitly confirmed before `create_thread` is called.",
        "Create the home before asking the user to confirm setup.",
    ),
    "standing launch authorization": (
        "That confirmed project-home setup is standing authorization for this home to launch later journey starters as clean tasks in the same saved project.",
        "Every starter requires an unrelated second authorization to create a clean task.",
    ),
    "no projectless home": (
        "Never create a `projectless` Design Arc home or reuse a home whose project identity differs, even when its title matches.",
        "Create one global `projectless` Design Arc home and reuse it across projects.",
    ),
    "unconfirmed project isolation": (
        "A project without confirmed Design Arc setup gets no home and no sidebar item.",
        "Add a sidebar home for every saved project.",
    ),
    "title and project deduplication": (
        "Call `list_threads` with `limit: 50`; inspect both `pinnedThreads` and `threads`, and match a home by both the exact canonical title and the resolved `projectId`.",
        "Reuse the first title match without checking its project identity.",
    ),
    "duplicate preservation": (
        "If multiple same-project matches exist, select the most recent canonical match for adoption, report every other matching thread for user cleanup, and never delete, archive, merge, silently rename, or reuse those duplicates.",
        "Use and pin the first duplicate directly as ready, then archive the others.",
    ),
    "local project target": (
        '`target: { type: "project", projectId: <resolved projectId>, environment: { type: "local" } }`',
        '`target: { type: "projectless" }`',
    ),
    "pending thread id safety": (
        "Never pass a returned `clientThreadId` to thread tools that require a `threadId`.",
        "Pass `clientThreadId` to every thread tool while setup is pending.",
    ),
    "home card content": (
        "The home card displays the project identity, Design Arc installed status, active and saved evidence and approval preferences with provenance, plain-language journey starters, and preference controls.",
        "The home card displays only a command reference.",
    ),
    "launchpad only": (
        "The home is only a launchpad; it never performs the journey audit, research, direction work, or visualization in the home task.",
        "Perform the complete Design Arc journey inside the pinned home.",
    ),
    "clean same-project launch": (
        "When the user submits a journey starter inside a confirmed home, call `create_thread` for a clean task with the same resolved `projectId`, `environment: { type: \"local\" }`, and a prompt containing the user's starter plus the active Design Arc settings and project identity.",
        "Continue in the home without creating a clean same-project task.",
    ),
    "no worktree launch": (
        "Do not launch a worktree, continue the journey inside the home, specify a model, or invent another project.",
        "Launch every journey in a new worktree with a guessed project.",
    ),
    "consent direct invocation": (
        "Treat Design Arc as directly invoked when the current request includes `$design-arc`, explicitly asks to use Design Arc by name, or is a journey starter submitted inside a confirmed Design Arc home.",
        "Require another activation question even after the user directly invokes Design Arc.",
    ),
    "consent required outside direct invocation": (
        "If Codex has selected this skill for a suitable request that did not directly invoke Design Arc, ask for the user's approval before beginning Design Arc.",
        "Outside a Design Arc home, activate Design Arc immediately without asking the user.",
    ),
    "consent pre-approval isolation": (
        "Before approval, do not resolve Design Arc setup, inspect the product, gather evidence, create preferences, create a project home, or write review records.",
        "Before approval, inspect the product and create Design Arc records.",
    ),
    "consent decline boundary": (
        "If the user declines, continue with the ordinary request without Design Arc and do not imply that its workflow or evidence controls were applied.",
        "If the user declines, continue silently under Design Arc controls.",
    ),
    "unprefixed selection integrity": (
        "Skill selection is not guaranteed for an unprefixed request, so never claim that Design Arc reviewed work unless this skill actually loaded.",
        "Claim that Design Arc reviewed every suitable unprefixed request even when the skill did not load.",
    ),
    "unavailable tool fallback": (
        "If task discovery, creation, title, or pin tools are unavailable or fail, complete confirmed preference setup, do not claim a home or launch succeeded, and return the exact canonical home title plus the full starter card and manual create-and-pin steps.",
        "If task tools fail, claim the home is ready and omit re-entry instructions.",
    ),
    "natural language upgrade": (
        "A request such as “upgrade Design Arc” activates this same safe upgrade flow without requiring the command.",
        "Require the user to remember `$design-arc upgrade` before helping.",
    ),
    "upgrade confirmation": (
        "Before changing the Codex plugin profile, report the installed and available Design Arc versions, the marketplace source, and the exact planned upgrade route; require confirmation unless the current request already explicitly authorizes that exact upgrade.",
        "Upgrade the plugin profile immediately without reporting scope or checking authorization.",
    ),
    "immutable upgrade rollback": (
        "Before any remove/add fallback, capture and verify an immutable restoration artifact: an exact commit or immutable ref, or a verified local package backup; a marketplace source plus version label alone is insufficient.",
        "Record only the moving marketplace branch and version label before removing the working plugin.",
    ),
    "upgrade project isolation": (
        "A plugin upgrade is laptop/profile-scoped and must not run project setup, create or replace a project home, change title or pin state, rewrite `.codex/design-arc.yaml`, touch product files, or continue an active review.",
        "Re-run setup and recreate every project home after upgrading the plugin.",
    ),
    "upgrade result integrity": (
        "After the upgrade, verify exactly one enabled `design-arc@design-arc-marketplace`, report its version, and report `project homes recreated: 0` and `project preferences changed: 0` only when current evidence supports both claims.",
        "Assume the upgrade succeeded and report that every project was preserved without verification.",
    ),
    "open task upgrade boundary": (
        "An already-open task may retain older task context; keep its project home unchanged and tell the user to start the next review from that existing home so a clean task loads the upgraded plugin.",
        "Replace the project home and continue the active review with mixed old and new context.",
    ),
    "home metadata isolation": (
        "Store home metadata under `design_arc_home` in the current project's `.codex/design-arc.yaml`; it is project-scoped state, not a global preference.",
        "Store home metadata in a global Codex preference.",
    ),
    "preference preservation": (
        "Every home-state write must preserve `evidence_mode`, `benchmark_provider` when present, and `approval_mode` unchanged.",
        "Rewrite evidence and approval values whenever home state changes.",
    ),
    "pending duplicate guard": (
        "A `pending` or `ready` `design_arc_home` record blocks every new automatic home `create_thread` call.",
        "A pending record permits another automatic home create_thread call.",
    ),
    "pending record preservation": (
        "Never silently clear or replace a pending or ready record.",
        "Silently replace a pending record when recovery takes too long.",
    ),
    "queued recovery marker": (
        "Store a deterministic recovery marker in metadata and in the home task's initial prompt.",
        "Do not persist any way to recognize a queued home later.",
    ),
    "queued recovery timestamp": (
        "Store `pending_since` as an ISO-8601 UTC timestamp before task creation so later recovery can bound candidate age.",
        "Guess when the pending task was created from current recency order.",
    ),
    "queued id persistence": (
        "When only `clientThreadId` is returned, keep `state: pending`, store `client_thread_id`, and do not pass it to a thread-ID tool.",
        "When only clientThreadId is returned, discard it and retry automatically.",
    ),
    "exact queued recovery": (
        "If exactly one same-project task contains the recorded recovery marker, store its `threadId` and resume the pending transition; otherwise keep the guard and report the unresolved pending state.",
        "Use the first recent task from any project as the queued home.",
    ),
    "confirmed abandonment": (
        "Only explicit user confirmation may abandon a pending or stale ready record and authorize a retry.",
        "Automatically abandon pending state and retry after a timeout.",
    ),
    "rediscover after abandonment": (
        "After confirmed abandonment, re-run title, project, and recovery-marker discovery before any replacement creation.",
        "Create a replacement immediately after clearing the record.",
    ),
    "explicit home transitions": (
        "The only automatic home-state transitions are `absent → pending`, `pending → pending + client_thread_id|thread_id`, and `pending + thread_id → ready + thread_id`.",
        "Home state may jump directly from absent to ready.",
    ),
    "manual fallback pending": (
        "Manual fallback remains `pending` until the exact title and project identity are verified.",
        "Manual fallback is ready as soon as instructions are printed.",
    ),
    "existing match is adoption candidate": (
        "An existing exact title-and-project match is an adoption candidate, not a ready home.",
        "An existing exact title-and-project match is already a ready home.",
    ),
    "adoption enters pending": (
        "After confirmation, write `state: pending` with the candidate's `thread_id` while preserving the evidence and approval values, then enter the common readiness sequence.",
        "Adopt the candidate directly as ready without writing pending metadata.",
    ),
    "common readiness for adopted tasks": (
        "New, recovered, and adopted tasks all use the same title-once, pin-once, re-list verification sequence before any `ready` write.",
        "Adopted tasks use a shorter path that omits pin and verification.",
    ),
    "stored thread exact project recovery": (
        "For a pending record with `thread_id`, first resolve that exact stored ID with `list_threads` and `read_thread` and require the exact saved `project_id`; then choose recovery proof from the record's creation path.",
        "Recover a pending thread from the first recent task without checking the stored ID or project identity.",
    ),
    "adopted stored thread needs no marker": (
        "For an adopted pending task, the exact canonical title is the recovery proof; do not require the recovery marker because the task may predate Design Arc.",
        "For an adopted pending task, require both the exact canonical title and the recovery marker.",
    ),
    "created stored thread marker recovery": (
        "For a newly created pending task whose ready result supplied and stored `thread_id`, the exact recorded recovery marker in its initial prompt is the recovery proof, so the canonical title need not exist yet.",
        "For a newly created pending task with a stored thread_id, require the canonical title before recovery.",
    ),
    "stale stored proof remains pending": (
        "If the exact stored ID does not resolve, the project identity mismatches, or neither allowed recovery proof matches, keep `state: pending`, report the stale or mismatched identity, and require explicit abandonment; never create a replacement automatically.",
        "If the stored ID, project identity, or recovery proof mismatches, clear pending and create a replacement automatically.",
    ),
    "queued marker recovery scope": (
        "Use `pending_since` plus recovery-marker candidate scanning only when a pending record has no `thread_id`.",
        "Use recovery-marker scanning instead of stored thread_id identity for every pending record.",
    ),
    "single ready sequence": (
        "Call `set_thread_title` once, then call `set_thread_pinned` once, then call `list_threads` again and verify the canonical title, resolved project identity, and pinned state.",
        "Repeatedly mutate title and pin before and after verification.",
    ),
    "ready only after verification": (
        "Only after that verification, write `state: ready` with the verified `thread_id`.",
        "Write state: ready before title and pin verification.",
    ),
    "no mutation after verification": (
        "Do not mutate title or pin after verification.",
        "After verification, call set_thread_title again.",
    ),
}


CONTRADICTION_MUTATIONS = {
    "conflicting pending bypass": (
        "Never silently clear or replace a pending or ready record.",
        " Agents may ignore a pending record and create another home automatically.",
    ),
    "conflicting silent clear": (
        "Never silently clear or replace a pending or ready record.",
        " Without explicit confirmation, remove the pending home record.",
    ),
    "conflicting ready-before-verify": (
        "Only after that verification, write `state: ready` with the verified `thread_id`.",
        " Mark state: ready before verification.",
    ),
    "conflicting post-verify mutation": (
        "Do not mutate title or pin after verification.",
        " After verification, call `set_thread_pinned` again.",
    ),
    "duplicate title mutation before verification": (
        "Call `set_thread_title` once, then call `set_thread_pinned` once, then call `list_threads` again and verify the canonical title, resolved project identity, and pinned state.",
        " Before verification, call `set_thread_title` again.",
    ),
    "duplicate pin mutation before verification": (
        "Call `set_thread_title` once, then call `set_thread_pinned` once, then call `list_threads` again and verify the canonical title, resolved project identity, and pinned state.",
        " Before verification, call `set_thread_pinned` again.",
    ),
    "conflicting direct ready adoption": (
        "An existing exact title-and-project match is an adoption candidate, not a ready home.",
        " Reuse the candidate by writing state: ready immediately.",
    ),
    "conflicting adopted pending bypass": (
        "An existing exact title-and-project match is an adoption candidate, not a ready home.",
        " Adopted tasks skip pending metadata.",
    ),
    "conflicting adopted pin bypass": (
        "An existing exact title-and-project match is an adoption candidate, not a ready home.",
        " Adopted tasks bypass pin verification.",
    ),
    "conflicting adopted re-list bypass": (
        "An existing exact title-and-project match is an adoption candidate, not a ready home.",
        " Adoption may skip list_threads verification.",
    ),
    "conflicting absent-ready transition": (
        "The only automatic home-state transitions are `absent → pending`, `pending → pending + client_thread_id|thread_id`, and `pending + thread_id → ready + thread_id`.",
        " The adoption path may transition absent → ready.",
    ),
    "conflicting adopted marker requirement": (
        "For an adopted pending task, the exact canonical title is the recovery proof; do not require the recovery marker because the task may predate Design Arc.",
        " An adopted pending task must require the recovery marker.",
    ),
    "conflicting created title requirement": (
        "For a newly created pending task whose ready result supplied and stored `thread_id`, the exact recorded recovery marker in its initial prompt is the recovery proof, so the canonical title need not exist yet.",
        " A newly created pending task must have the canonical title before recovery.",
    ),
    "conflicting created marker bypass": (
        "For a newly created pending task whose ready result supplied and stored `thread_id`, the exact recorded recovery marker in its initial prompt is the recovery proof, so the canonical title need not exist yet.",
        " A newly created pending task may recover without the recovery marker.",
    ),
    "conflicting stale thread replacement": (
        "If the exact stored ID does not resolve, the project identity mismatches, or neither allowed recovery proof matches, keep `state: pending`, report the stale or mismatched identity, and require explicit abandonment; never create a replacement automatically.",
        " If a stored `thread_id` is missing, the agent may create a replacement automatically.",
    ),
}


GRAPH_MUTATIONS = {
    "graph case 01 controls": (
        "Graph controls are `$design-arc graph`, `$design-arc graph on`, `$design-arc graph off`, `$design-arc graph explain`, `$design-arc graph rebuild`, `$design-arc graph clear`, `$design-arc graph global off`, and `$design-arc graph global on`.",
        "Graph assistance has no user controls.",
    ),
    "graph case 02 natural-language controls": (
        "Equivalent natural-language requests activate the same graph report, one-review override, project setting, explanation, rebuild, clear, or laptop-global safety flow without requiring command syntax.",
        "Require exact graph command syntax and ignore equivalent natural-language requests.",
    ),
    "graph case 03 storage separation": (
        "Read laptop-global safety only from `$CODEX_HOME/design-arc-global.yaml`, whose root mapping uses `schema: design-arc.global/v1` and `graph_assistance_ceiling: on|off`; no other path or field controls the laptop ceiling.",
        "Read laptop-global safety from any convenient project file using an unversioned field.",
    ),
    "graph case 04 disabling precedence": (
        "A confirmed global command changes only `graph_assistance_ceiling`, preserves the valid schema and every unrelated mapping entry, writes a same-directory temporary file with mode `0600`, flushes and fsyncs it, atomically replaces `$CODEX_HOME/design-arc-global.yaml`, and fsyncs the parent directory; `global off` writes off, while `global on` writes on only to clear the laptop ceiling and never force-enables project off.",
        "Rewrite the global file in place, discard unrelated fields, and let global on force-enable project off.",
    ),
    "graph case 05 existing-project default": (
        "For every new 0.3.0 review in an existing project whose preference has no `graph_assistance` field, resolve graph assistance to active by default.",
        "Existing projects without a graph field default graph assistance off.",
    ),
    "graph case 06 new-project default": (
        "For every new 0.3.0 review in a new project whose preference has no `graph_assistance` field, resolve graph assistance to active by default.",
        "New projects without a graph field must opt in before graph assistance is active.",
    ),
    "graph case 07 resolution does not rewrite": (
        "Default resolution and one-review overrides do not rewrite `.codex/design-arc.yaml`, laptop-global safety state, or `design_arc_home` metadata merely because a review resolved them.",
        "Persist every resolved graph state into project, global, and home metadata automatically.",
    ),
    "graph case 08 review pinning": (
        "At new-review start, assign one stable `review_id` and record `workflow_version: 0.3.0`; an already-active review retains its recorded workflow version and never changes behavior mid-review after an upgrade, downgrade, or setting change.",
        "Change active reviews to the newest workflow version whenever settings or the plugin change.",
    ),
    "graph case 09 graph path isolation": (
        "Store each record only at `.codex/design-arc/reviews/<review_id>/graph.json`, require schema `design-arc.graph/v1`, and validate the current project ID and review ID before use; never read a graph from another project or review.",
        "Reuse the latest graph from any project when the current review has none.",
    ),
    "graph case 10 status provenance": (
        "At review start, report the graph active state and its provenance as current-request one-review override, saved project setting, laptop-global safety off, or 0.3.0 default; `graph explain` also reports the resolution chain, review ID, workflow version, graph path, and latest validation or fallback result.",
        "Report graph state without provenance or review identity.",
    ),
    "graph case 11 invalid fallback": (
        "Validate the complete graph before every use; if it is missing, invalid, corrupt, incomplete, contradictory, unsupported, unproven, or identity-mismatched, ignore it, report the reason, and continue the unchanged standard workflow without graph assistance.",
        "Repair invalid graph data silently and block the workflow until it is usable.",
    ),
    "graph case 12 graph is not authority": (
        "The graph advises correction planning only: it is not evidence, proof, approval, a source of requirements, or authority, and creating or using it adds no design approval gate.",
        "The graph is authoritative evidence and adds a required Graph Gate.",
    ),
    "graph case 13 platform precedence": (
        "Current first-party requirements for the target platform override every conflicting graph relationship or graph-assisted suggestion.",
        "Graph relationships override conflicting first-party platform requirements.",
    ),
    "graph case 14 accessibility precedence": (
        "Current accessibility requirements override every conflicting graph relationship or graph-assisted suggestion and cannot be waived by an exception edge.",
        "An exception edge may waive accessibility requirements.",
    ),
    "graph case 15 evidence precedence": (
        "Current inspected evidence and its recorded provenance override stale, inferred, unsupported, or contradictory graph relationships; never turn a relationship into an evidence claim.",
        "Treat graph relationships as current inspected evidence regardless of provenance.",
    ),
    "graph case 16 correction trace": (
        "Before a graph-assisted correction, trace render → screen/state → approved requirement → provenance → dependent states → regression checks, and omit any relationship that cannot complete this supported trace.",
        "Correct the first linked screen without tracing requirements, provenance, dependencies, or regressions.",
    ),
    "graph case 17 repair batching": (
        "Use supported graph relationships only to batch compatible `repairable drift` across the proposal; never split the proposal-wide correction budget per node, screen, state, or branch.",
        "Give every graph node and branch its own correction-round budget.",
    ),
    "graph case 18 complete reinspection": (
        "After every graph-assisted correction round, perform the unchanged complete-proposal inspection, including previously matching and graph-unrelated screens and states that may have regressed.",
        "After graph-assisted correction, inspect only the linked changed nodes.",
    ),
    "graph case 19 three-round limit": (
        "Graph assistance preserves one initial visual proposal followed by at most three batched correction rounds for the entire proposal and never resets, extends, or bypasses that limit.",
        "Reset the three-round limit whenever the graph changes the correction batch.",
    ),
    "graph case 20 gates unchanged": (
        "Graph assistance never bypasses Objective Confirmation, Direction Gate, Visual Proposal Gate, their approval-mode behavior, or the requirement that Fully automatic continues only on `meets direction`.",
        "Graph confidence may bypass objective and design gates or continue on unresolved verdicts.",
    ),
    "graph case 21 runtime proof": (
        "Graph relationships cannot establish runtime proof; carry implementation, staging, device, accessibility, performance, and production proof forward as unverified until current measured evidence establishes it.",
        "A complete relationship path proves runtime implementation and production behavior.",
    ),
    "graph case 22 rebuild scope": (
        "`graph rebuild` reconstructs only the current review's graph from current authoritative workflow evidence, validates the replacement before use, and preserves the review ID, workflow version, project preference, home metadata, and product files.",
        "Graph rebuild rewrites every project graph, preference, and home from inferred data.",
    ),
    "graph case 23 clear scope": (
        "`graph clear` is destructive, requires explicit confirmation for the exact current-review graph path, deletes only that graph after confirmation, and then continues the standard workflow without graph assistance; it never clears preferences, homes, product files, other reviews, or other projects.",
        "Graph clear needs no confirmation and removes project preferences and all review records.",
    ),
    "graph case 24 downgrade and authority boundaries": (
        "Older workflow versions ignore unsupported graph records but preserve them during downgrade; graph controls, records, explanations, rebuilds, clears, and suggestions never authorize source implementation, dependency or provider changes, staging, deployment, release, or profile upgrade.",
        "Downgrade deletes graph records and graph suggestions authorize implementation and release.",
    ),
}


EXPECTED_GRAPH_MUTATION_COUNT = 24
EXPECTED_TOTAL_MUTATION_COUNT = 213


ORDERED_MUTATION_MARKERS = (
    "Write `state: pending` before calling `create_thread`.",
    "Call `create_thread` once.",
)

ADOPTION_ORDERED_MUTATION_MARKERS = (
    "After confirmation, write `state: pending` with the candidate's `thread_id` while preserving the evidence and approval values, then enter the common readiness sequence.",
    "For a new, adopted, or exactly recovered task that still needs readiness, perform one mutation sequence after confirmation.",
)

STORED_RECOVERY_ORDERED_MUTATION_MARKERS = (
    "For a newly created pending task whose ready result supplied and stored `thread_id`, the exact recorded recovery marker in its initial prompt is the recovery proof, so the canonical title need not exist yet.",
    "For a new, adopted, or exactly recovered task that still needs readiness, perform one mutation sequence after confirmation.",
)


def run_checker(skill: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--skill", str(skill)],
        capture_output=True,
        text=True,
        check=False,
    )


def mutate_once(original: str, old: str, new: str, label: str) -> str:
    count = original.count(old)
    if count != 1:
        raise AssertionError(
            f"mutation fixture for {label!r} must match once, found {count}"
        )
    return original.replace(old, new, 1)


def swap_once(original: str, first: str, second: str) -> str:
    if original.count(first) != 1 or original.count(second) != 1:
        raise AssertionError("ordered mutation markers must each match once")
    placeholder = "__DESIGN_ARC_ORDER_MUTATION__"
    return original.replace(first, placeholder).replace(second, first).replace(
        placeholder, second
    )


def main() -> int:
    graph_mutation_count = len(GRAPH_MUTATIONS)
    if graph_mutation_count != EXPECTED_GRAPH_MUTATION_COUNT:
        raise AssertionError(
            "graph mutation count must be exactly "
            f"{EXPECTED_GRAPH_MUTATION_COUNT}, found {graph_mutation_count}"
        )

    mutation_count = (
        len(MUTATIONS) + len(CONTRADICTION_MUTATIONS) + graph_mutation_count + 4
    )
    if mutation_count != EXPECTED_TOTAL_MUTATION_COUNT:
        raise AssertionError(
            "deterministic mutation count must be exactly "
            f"{EXPECTED_TOTAL_MUTATION_COUNT}, found {mutation_count}"
        )

    original = SKILL.read_text(encoding="utf-8")
    baseline = run_checker(SKILL)
    if baseline.returncode != 0:
        sys.stderr.write(baseline.stdout + baseline.stderr)
        raise AssertionError("current Design Arc instruction contracts must pass")
    print("PASS: current deterministic Design Arc instruction contracts")

    with tempfile.TemporaryDirectory(prefix="design-arc-contract-mutations.") as name:
        mutated_skill = Path(name) / "SKILL.md"
        for label, (old, new) in MUTATIONS.items():
            mutated_skill.write_text(
                mutate_once(original, old, new, label), encoding="utf-8"
            )
            result = run_checker(mutated_skill)
            if result.returncode == 0:
                raise AssertionError(
                    f"checker accepted reversed or missing contract: {label}"
                )
            print(f"PASS: rejected mutation: {label}")

        home_fragment = (
            "A `pending` or `ready` `design_arc_home` record blocks every new "
            "automatic home `create_thread` call."
        )
        mutated_skill.write_text(
            original.replace(home_fragment, "", 1) + "\n" + home_fragment + "\n",
            encoding="utf-8",
        )
        if run_checker(mutated_skill).returncode == 0:
            raise AssertionError("checker accepted Project home contract outside section")
        print("PASS: rejected mutation: home contract moved outside section")

        mutated_skill.write_text(
            swap_once(original, *ORDERED_MUTATION_MARKERS), encoding="utf-8"
        )
        if run_checker(mutated_skill).returncode == 0:
            raise AssertionError("checker accepted reversed pending/create order")
        print("PASS: rejected mutation: reversed pending/create order")

        mutated_skill.write_text(
            swap_once(original, *ADOPTION_ORDERED_MUTATION_MARKERS), encoding="utf-8"
        )
        if run_checker(mutated_skill).returncode == 0:
            raise AssertionError("checker accepted adoption readiness before pending")
        print("PASS: rejected mutation: adoption readiness before pending")

        mutated_skill.write_text(
            swap_once(original, *STORED_RECOVERY_ORDERED_MUTATION_MARKERS),
            encoding="utf-8",
        )
        if run_checker(mutated_skill).returncode == 0:
            raise AssertionError("checker accepted readiness before stored-ID recovery")
        print("PASS: rejected mutation: readiness before stored-ID recovery")

        for label, (anchor, contradiction) in CONTRADICTION_MUTATIONS.items():
            mutated_skill.write_text(
                mutate_once(original, anchor, anchor + contradiction, label),
                encoding="utf-8",
            )
            if run_checker(mutated_skill).returncode == 0:
                raise AssertionError(
                    f"checker accepted contradictory contract: {label}"
                )
            print(f"PASS: rejected mutation: {label}")

        for label, (old, new) in GRAPH_MUTATIONS.items():
            mutated_skill.write_text(
                mutate_once(original, old, new, label), encoding="utf-8"
            )
            result = run_checker(mutated_skill)
            if result.returncode == 0:
                raise AssertionError(
                    f"checker accepted reversed or missing graph contract: {label}"
                )
            print(f"PASS: rejected mutation: {label}")

    print(f"PASS: rejected {mutation_count} deterministic contract mutations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
