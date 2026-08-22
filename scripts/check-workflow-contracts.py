#!/usr/bin/env python3
"""Check deterministic contracts encoded by the Design Arc skill.

This validator checks the written instruction contract. It does not execute or
simulate an agent; fresh-context scenarios provide separate behavioral evidence.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SKILL = REPO_ROOT / "plugins/design-arc/skills/design-arc/SKILL.md"


REQUIRED_CONTRACTS = {
    "setup and objective ordering": (
        "Resolve setup before product inspection, external research, or generation. Then establish the user's objective before any of those activities.",
    ),
    "setup and mode commands": (
        "`$design-arc setup`",
        "`$design-arc home`",
        "`$design-arc evidence benchmarks`",
        "`$design-arc evidence guidelines`",
        "`$design-arc mode`",
        "`$design-arc mode guided`",
        "`$design-arc mode follow-recommendation`",
        "`$design-arc mode fully-automatic`",
    ),
    "preference precedence": (
        "1. Explicit one-run override in the current request; do not save it unless asked.",
        "2. Saved `.codex/design-arc.yaml` value.",
        "3. Confirmed legacy import, only when the new file is absent.",
        "4. First-use selection for every choice still missing.",
    ),
    "independent provenance": (
        "Always report the active evidence mode and approval mode, and the provenance of each independently.",
    ),
    "two-step first-use setup": (
        "Collect first-use evidence and approval choices in two separate user turns. Never present both choice lists in the same message.",
        "**Step 1 — evidence.** Present exactly this numbered choice first:",
        "**Guidelines + Mobbin benchmarks — recommended.**",
        "Ensure you have an active Mobbin Pro account before choosing this option",
        "Ask the user to reply with `1` or `2`.",
        "**Step 2 — approval.** Only after evidence is resolved, present this separate numbered choice:",
        "Ask the user to reply with `1`, `2`, or `3`.",
    ),
    "six mode combinations": (
        "| Guidelines + Benchmarks | Guided | Direction Gate stops; Visual Proposal Gate stops |",
        "| Guidelines + Benchmarks | Follow recommendation | Direction Gate continues with the marked recommendation; Visual Proposal Gate stops |",
        "| Guidelines + Benchmarks | Fully automatic | Direction Gate continues; Visual Proposal Gate continues only on `meets direction` |",
        "| Guidelines only | Guided | Direction Gate stops; Visual Proposal Gate stops |",
        "| Guidelines only | Follow recommendation | Direction Gate continues with the marked recommendation; Visual Proposal Gate stops |",
        "| Guidelines only | Fully automatic | Direction Gate continues; Visual Proposal Gate continues only on `meets direction` |",
    ),
    "benchmark evidence quality": (
        "Inspect complete, relevant real-product journeys and explain why each selected pattern is useful for the established objective.",
        "Library presence, metadata, popularity, or one screenshot never proves best-in-class quality.",
    ),
    "guidelines isolation": (
        "In Guidelines only mode, perform no benchmark lookup and make no benchmark-evidence claim.",
    ),
    "missing benchmark access": (
        "If benchmark access is missing, stop; never degrade silently.",
        "Offer either a one-run Guidelines only fallback that does not rewrite the saved preference, or a confirmed saved switch to Guidelines only.",
    ),
    "legacy preference mapping": (
        "`.codex/fb-ux.yaml` maps to `evidence_mode: benchmarks`, `benchmark_provider: mobbin`, and its preserved approval mode.",
        "`.codex/apple-guidelines-stitch.yaml` maps to `evidence_mode: guidelines`, omits `benchmark_provider`, and preserves its approval mode.",
        "Show the proposed mapping and ask once before importing it.",
        "If both legacy files exist, present both mappings and require the user to choose one or start fresh.",
        "Never silently merge, rewrite, or delete either legacy preference file.",
    ),
    "objective handling": (
        "In Guided or Follow recommendation mode, restate a stated objective and ask the user to confirm or revise it.",
        "Fully automatic may skip the objective pause only when the current request states an explicit objective.",
        "If the objective is missing or materially ambiguous, stop and ask; never invent it.",
    ),
    "direction gate": (
        "At the Direction Gate, present one unmistakably marked recommendation plus meaningful alternatives and their trade-offs.",
    ),
    "stitch gate": (
        "Fully automatic continues only when the visual verdict is `meets direction`; `meets with corrections` and `does not meet` both stop.",
    ),
    "platform precedence": (
        "For Android or web targets, current first-party platform rules override conflicting Apple-inspired judgment.",
    ),
    "evidence integrity": (
        "Do not claim product inspection, first-party guidance, benchmark evidence, or new generated output without current evidence for that exact claim.",
    ),
    "authorization boundary": (
        "Design approval never authorizes source implementation, staging, live deployment, release, destructive changes, provider changes, or work outside the authorized integration lane.",
    ),
    "renderer choice and default": (
        "Confirm that the active host is Codex before recommending a visualization path.",
        "Create static screen images and complete journey boards directly in Codex by default.",
        "Google Stitch is valuable for canvas-based editing, multiple visual alternatives, and sustained visual refinement.",
        "Recommend Stitch when those benefits materially help the review, while keeping direct Codex generation as the default.",
        "Stitch remains optional and separately authorized.",
    ),
    "low-threshold Stitch recommendation": (
        "Recommend Stitch when any one genuine trigger occurs: a second meaningful visual direction; a change spanning three or more screens; precise layout, spacing, or styling iteration; user-directed canvas editing; likely continuation on another day; a journey becoming difficult to review as one board; noticeable unrelated drift after one Codex correction round; device variants; collaboration; or design export.",
        "The first recommendation names the specific benefit; a later recommendation is brief and appears only after another genuine trigger or materially larger scope.",
    ),
    "Stitch recommendation control": (
        "When Stitch is recommended, present this numbered choice:",
        "1. **Stitch** (recommended)",
        "2. **Stay in Codex**",
        "3. **Both**",
        "Reply with `1`, `2`, or `3`.",
        "Both means create the Codex board and the Stitch visual workspace from the same approved journey.",
        "A Stitch recommendation is advisory: never transfer automatically, and continuing in Codex remains available.",
        "Treat `stay in Codex` as a choice for the current editing phase, not a permanent suppression.",
        "If the user says not to recommend Stitch again for this review, suppress every further Stitch recommendation for that review.",
    ),
    "renderer-neutral validation": (
        "Before using Stitch, prepare the complete evidence-grounded journey, requirements, and important-state inventory.",
        "Stitch is a visualization tool, not an evidence authority.",
        "The active host must validate returned screens and apply the existing proposal-wide correction loop of up to three correction rounds.",
    ),
    "project home resolution": (
        "Call `list_projects` before any home lookup or creation and resolve the current saved project's `projectId` and saved-project name; use the workspace-folder name only when the saved-project name is unavailable.",
        "The canonical title is `Design Arc — <Project Name>`.",
    ),
    "project home confirmation": (
        "Home creation must be part of the setup proposal and must be explicitly confirmed before `create_thread` is called.",
        "That confirmed project-home setup is standing authorization for this home to launch later journey starters as clean tasks in the same saved project.",
    ),
    "project home isolation": (
        "Never create a `projectless` Design Arc home or reuse a home whose project identity differs, even when its title matches.",
        "A project without confirmed Design Arc setup gets no home and no sidebar item.",
    ),
    "project home deduplication": (
        "Call `list_threads` with `limit: 50`; inspect both `pinnedThreads` and `threads`, and match a home by both the exact canonical title and the resolved `projectId`.",
        "If multiple same-project matches exist, select the most recent canonical match for adoption, report every other matching thread for user cleanup, and never delete, archive, merge, silently rename, or reuse those duplicates.",
    ),
    "project home task creation": (
        '`target: { type: "project", projectId: <resolved projectId>, environment: { type: "local" } }`',
        "Never pass a returned `clientThreadId` to thread tools that require a `threadId`.",
    ),
    "project home launchpad content": (
        "The home card displays the project identity, Design Arc installed status, active and saved evidence and approval preferences with provenance, plain-language journey starters, and preference controls.",
        "The home is only a launchpad; it never performs the journey audit, research, direction work, or visualization in the home task.",
    ),
    "clean journey task launch": (
        "When the user submits a journey starter inside a confirmed home, call `create_thread` for a clean task with the same resolved `projectId`, `environment: { type: \"local\" }`, and a prompt containing the user's starter plus the active Design Arc settings and project identity.",
        "Do not launch a worktree, continue the journey inside the home, specify a model, or invent another project.",
    ),
    "consent-gated activation": (
        "Treat Design Arc as directly invoked when the current request includes `$design-arc`, explicitly asks to use Design Arc by name, or is a journey starter submitted inside a confirmed Design Arc home.",
        "If Codex has selected this skill for a suitable request that did not directly invoke Design Arc, ask for the user's approval before beginning Design Arc.",
        "Before approval, do not resolve Design Arc setup, inspect the product, gather evidence, create preferences, create a project home, or write review records.",
        "If the user declines, continue with the ordinary request without Design Arc and do not imply that its workflow or evidence controls were applied.",
        "Skill selection is not guaranteed for an unprefixed request, so never claim that Design Arc reviewed work unless this skill actually loaded.",
    ),
    "task tool fallback": (
        "If task discovery, creation, title, or pin tools are unavailable or fail, complete confirmed preference setup, do not claim a home or launch succeeded, and return the exact canonical home title plus the full starter card and manual create-and-pin steps.",
    ),
    "safe plugin upgrade": (
        "`$design-arc upgrade`",
        "A request such as “upgrade Design Arc” activates this same safe upgrade flow without requiring the command.",
        "Before changing the Codex plugin profile, report the installed and available Design Arc versions, the marketplace source, and the exact planned upgrade route; require confirmation unless the current request already explicitly authorizes that exact upgrade.",
        "Before any remove/add fallback, capture and verify an immutable restoration artifact: an exact commit or immutable ref, or a verified local package backup; a marketplace source plus version label alone is insufficient.",
        "A plugin upgrade is laptop/profile-scoped and must not run project setup, create or replace a project home, change title or pin state, rewrite `.codex/design-arc.yaml`, touch product files, or continue an active review.",
        "After the upgrade, verify exactly one enabled `design-arc@design-arc-marketplace`, report its version, and report `project homes recreated: 0` and `project preferences changed: 0` only when current evidence supports both claims.",
        "An already-open task may retain older task context; keep its project home unchanged and tell the user to start the next review from that existing home so a clean task loads the upgraded plugin.",
    ),
}


MOTION_CONTRACT_CASES = {
    "case 01 evidence precedence": (
        "Use this motion-evidence precedence: existing product motion; native platform behavior and standard components; current first-party platform guidance; inspected relevant shipped-product motion; labeled Design Arc judgment.",
    ),
    "case 02 benchmark and static limits": (
        "In Guidelines + Benchmarks mode, authorized shipped-product motion may be inspected as precedent.",
        "Static screens or sequences support only start/end state, changing element, journey location, and transition intent; they cannot support exact duration, easing, springs, velocity, interruption, or choreography.",
    ),
    "case 03 playable evidence record": (
        "For playable motion evidence, record source; product/journey; frame rate when known; observed duration/path/order; interruption/reversal; measurement method; confidence; and missing states. Frame-derived values are estimates.",
    ),
    "case 04 temporal claim labels": (
        "Every temporal claim uses exactly one label: `directly observed`, `measured estimate`, `pattern-level inference`, `Design Arc judgment`, or `unverified`.",
    ),
    "case 05 unavailable playable evidence": (
        "When necessary playable evidence is unavailable, report the limitation and offer an accessible live product, user recording, authorized Page Flows recording, native default, or labeled proposal requiring implementation validation. Never invent it.",
    ),
    "case 06 Guidelines isolation": (
        "In Guidelines only mode, perform no benchmark lookup, make no real-product motion claim, and report that no benchmark motion was inspected.",
    ),
    "case 07 complete material motion contract": (
        "Every material motion contract includes: Motion ID; journey location; purpose; trigger; start/end state; spatial behavior; choreography; timing; easing/spring; interruption; reduced motion; evidence; provenance; implementation target; implementation source; proof status. Unsupported values are `unverified`.",
        "`implementation target` records the runtime and UI technology, such as Web, React, SwiftUI, UIKit, or Compose; record component and state-change specificity separately when useful.",
        "`timing` uses milliseconds or seconds for duration and delay, or records that a physical spring with explicit parameters governs timing.",
        "`easing/spring` records cubic-bezier coordinates, a named platform curve, or physical spring parameters such as mass, stiffness, damping, and initial velocity.",
        "`interruption` records whether motion can be interrupted or reversed, how cancellation resolves, and what happens on re-entry.",
        "`provenance` uses exactly one of `directly observed`, `measured estimate`, `pattern-level inference`, `Design Arc judgment`, or `unverified` for each claim, cites the supporting source, and records the measurement or estimate basis when applicable.",
        "`implementation source` names the existing product token, native or standard component, separately approved library, or custom implementation and records the authorizing owner; a proposal alone does not authorize it.",
        "`proof status` distinguishes `specified`, `prototyped`, `staging verified`, `device verified`, and `production verified` as applicable; use only the highest status established by current evidence.",
    ),
    "case 08 Motion+ boundary": (
        "Motion+ is never required by or evidence for Design Arc, and it is never a Design Arc dependency.",
        "An authorized implementation owner may separately approve Motion+ as an optional implementation dependency and implementation source; that approval does not install it or make it Design Arc evidence or authority.",
        "After separate authorization from the implementation owner, Motion+ assistance may cover documentation and example search; reusable source retrieval; spring and easing assistance; saved-transition inspection; performance auditing; and design-system adaptation.",
    ),
    "case 09 direction summary and least motion": (
        "At the Direction Gate, include a motion summary that identifies the material motion scope, retained native or existing behavior, proposed custom behavior, and unresolved evidence.",
        "Apply the least-motion principle: use no more motion than the stated interaction purpose requires, and remove decorative motion without a justified purpose.",
        "For each direction, explain the motion's concrete interaction purpose and why it uses no more motion than that purpose requires.",
        "For each direction, cite relevant inspected real-product evidence and current platform guidance, or state that either is unavailable.",
        "For each direction, apply the required provenance label to every temporal claim and distinguish directly observed behavior from measured estimates.",
        "For each direction, describe reduced-motion implications, motion-specific risks, and implementation complexity in the target stack.",
        "For each direction, identify what remains unproven and the staging, device, or production evidence needed to prove it.",
        "Headings or field names without these direction-specific explanations do not satisfy the Direction Gate.",
    ),
    "case 10 prototype, proof, and authority boundaries": (
        "Generated screens and design prototypes can illustrate states and transition intent but cannot prove timing, easing, springs, interruption, reduced-motion behavior, performance, or runtime implementation quality.",
        "Only measured staging or target-device behavior can establish implementation proof.",
        "Design Arc may specify and critique motion, but it does not authorize application-code implementation, dependency installation, staging, deployment, or release.",
        "Before assigning a visual verdict, explicitly evaluate motion purpose and least-motion restraint, provenance labels and citations, reduced-motion behavior, alignment with every material motion contract, prototype limitations, and remaining runtime proof.",
        "A `meets direction` verdict is valid only when the prototype aligns with those motion requirements within its capabilities and every limitation and remaining runtime proof item is documented; any unexplained gap yields `meets with corrections` or `does not meet`.",
        "Fully automatic may continue on `meets direction` only after this motion evaluation is recorded; it cannot waive a missing or contradictory motion check.",
    ),
    "case 11 motion run record": (
        "Relevant run records include motion scope, evidence, provenance, contracts, reduced motion, implementation source, proof, and remaining uncertainty.",
    ),
    "case 12 automatic evidence integrity": (
        "Fully automatic mode never bypasses motion evidence integrity.",
    ),
}


GRAPH_CONTRACT_CASES = {
    "case 01 controls": (
        "Graph controls are `$design-arc graph`, `$design-arc graph on`, `$design-arc graph off`, `$design-arc graph explain`, `$design-arc graph rebuild`, `$design-arc graph clear`, `$design-arc graph global off`, and `$design-arc graph global on`.",
    ),
    "case 02 natural-language controls": (
        "Equivalent natural-language requests activate the same graph report, one-review override, project setting, explanation, rebuild, clear, or laptop-global safety flow without requiring command syntax.",
    ),
    "case 03 storage separation": (
        "Save the project setting only as `graph_assistance: on|off` in that project's `.codex/design-arc.yaml`; keep laptop-global graph safety state isolated under the active Codex profile, never in a project or product file.",
        "Read laptop-global safety only from `$CODEX_HOME/design-arc-global.yaml`, whose root mapping uses `schema: design-arc.global/v1` and `graph_assistance_ceiling: on|off`; no other path or field controls the laptop ceiling.",
    ),
    "case 04 disabling precedence": (
        "Resolve graph assistance independently for a new review: an explicit one-review off override, project off, or global off each disables it; global on is only permission to resolve the project and can never force-enable project off.",
        "When the global file is absent, treat the ceiling as on without creating it; malformed YAML, a non-mapping root, a missing or unsupported schema, or a missing or invalid ceiling fails safe as global off, is reported, and is never rewritten merely by resolution.",
        "A confirmed global command changes only `graph_assistance_ceiling`, preserves the valid schema and every unrelated mapping entry, writes a same-directory temporary file with mode `0600`, flushes and fsyncs it, atomically replaces `$CODEX_HOME/design-arc-global.yaml`, and fsyncs the parent directory; `global off` writes off, while `global on` writes on only to clear the laptop ceiling and never force-enables project off.",
    ),
    "case 05 existing-project default": (
        "For every new 0.3.0 review in an existing project whose preference has no `graph_assistance` field, resolve graph assistance to active by default.",
    ),
    "case 06 new-project default": (
        "For every new 0.3.0 review in a new project whose preference has no `graph_assistance` field, resolve graph assistance to active by default.",
    ),
    "case 07 resolution does not rewrite": (
        "Default resolution and one-review overrides do not rewrite `.codex/design-arc.yaml`, laptop-global safety state, or `design_arc_home` metadata merely because a review resolved them.",
    ),
    "case 08 review pinning": (
        "At new-review start, assign one stable `review_id` and record `workflow_version: 0.3.0`; an already-active review retains its recorded workflow version and never changes behavior mid-review after an upgrade, downgrade, or setting change.",
    ),
    "case 09 graph path isolation": (
        "Store each record only at `.codex/design-arc/reviews/<review_id>/graph.json`, require schema `design-arc.graph/v1`, and validate the current project ID and review ID before use; never read a graph from another project or review.",
        "Resolve `scripts/validate-graph-record.py` relative to the directory containing this `SKILL.md`, never relative to the product workspace or repository root.",
    ),
    "case 10 status provenance": (
        "At review start, report the graph active state and its provenance as current-request one-review override, saved project setting, laptop-global safety off, or 0.3.0 default; `graph explain` also reports the resolution chain, review ID, workflow version, graph path, and latest validation or fallback result.",
    ),
    "case 11 invalid fallback": (
        "Validate the complete graph before every use; if it is missing, invalid, corrupt, incomplete, contradictory, unsupported, unproven, or identity-mismatched, ignore it, report the reason, and continue the unchanged standard workflow without graph assistance.",
    ),
    "case 12 graph is not authority": (
        "The graph advises correction planning only: it is not evidence, proof, approval, a source of requirements, or authority, and creating or using it adds no design approval gate.",
    ),
    "case 13 platform precedence": (
        "Current first-party requirements for the target platform override every conflicting graph relationship or graph-assisted suggestion.",
    ),
    "case 14 accessibility precedence": (
        "Current accessibility requirements override every conflicting graph relationship or graph-assisted suggestion and cannot be waived by an exception edge.",
    ),
    "case 15 evidence precedence": (
        "Current inspected evidence and its recorded provenance override stale, inferred, unsupported, or contradictory graph relationships; never turn a relationship into an evidence claim.",
    ),
    "case 16 correction trace": (
        "Before a graph-assisted correction, trace render → screen/state → approved requirement → provenance → dependent states → regression checks, and omit any relationship that cannot complete this supported trace.",
    ),
    "case 17 repair batching": (
        "Use supported graph relationships only to batch compatible `repairable drift` across the proposal; never split the proposal-wide correction budget per node, screen, state, or branch.",
    ),
    "case 18 complete reinspection": (
        "After every graph-assisted correction round, perform the unchanged complete-proposal inspection, including previously matching and graph-unrelated screens and states that may have regressed.",
    ),
    "case 19 three-round limit": (
        "Graph assistance preserves one initial visual proposal followed by at most three batched correction rounds for the entire proposal and never resets, extends, or bypasses that limit.",
    ),
    "case 20 gates unchanged": (
        "Graph assistance never bypasses Objective Confirmation, Direction Gate, Visual Proposal Gate, their approval-mode behavior, or the requirement that Fully automatic continues only on `meets direction`.",
    ),
    "case 21 runtime proof": (
        "Graph relationships cannot establish runtime proof; carry implementation, staging, device, accessibility, performance, and production proof forward as unverified until current measured evidence establishes it.",
    ),
    "case 22 rebuild scope": (
        "`graph rebuild` reconstructs only the current review's graph from current authoritative workflow evidence, validates the replacement before use, and preserves the review ID, workflow version, project preference, home metadata, and product files.",
    ),
    "case 23 clear scope": (
        "`graph clear` is destructive, requires explicit confirmation for the exact current-review graph path, deletes only that graph after confirmation, and then continues the standard workflow without graph assistance; it never clears preferences, homes, product files, other reviews, or other projects.",
    ),
    "case 24 downgrade and authority boundaries": (
        "Older workflow versions ignore unsupported graph records but preserve them during downgrade; graph controls, records, explanations, rebuilds, clears, and suggestions never authorize source implementation, dependency or provider changes, staging, deployment, release, or profile upgrade.",
    ),
}


PROJECT_HOME_HEADING = "### Project home"
PROJECT_HOME_MUTATION_HEADING = "#### Reuse, create, recover, and verify"

REQUIRED_PROJECT_HOME_CONTRACTS = {
    "home metadata isolation": (
        "Store home metadata under `design_arc_home` in the current project's `.codex/design-arc.yaml`; it is project-scoped state, not a global preference.",
        "Every home-state write must preserve `evidence_mode`, `benchmark_provider` when present, and `approval_mode` unchanged.",
    ),
    "pending duplicate guard": (
        "A `pending` or `ready` `design_arc_home` record blocks every new automatic home `create_thread` call.",
        "Never silently clear or replace a pending or ready record.",
    ),
    "queued recovery": (
        "Store `pending_since` as an ISO-8601 UTC timestamp before task creation so later recovery can bound candidate age.",
        "Store a deterministic recovery marker in metadata and in the home task's initial prompt.",
        "When only `clientThreadId` is returned, keep `state: pending`, store `client_thread_id`, and do not pass it to a thread-ID tool.",
        "If exactly one same-project task contains the recorded recovery marker, store its `threadId` and resume the pending transition; otherwise keep the guard and report the unresolved pending state.",
    ),
    "explicit abandonment": (
        "Only explicit user confirmation may abandon a pending or stale ready record and authorize a retry.",
        "After confirmed abandonment, re-run title, project, and recovery-marker discovery before any replacement creation.",
    ),
    "home state transitions": (
        "The only automatic home-state transitions are `absent → pending`, `pending → pending + client_thread_id|thread_id`, and `pending + thread_id → ready + thread_id`.",
        "Manual fallback remains `pending` until the exact title and project identity are verified.",
    ),
    "existing home adoption": (
        "An existing exact title-and-project match is an adoption candidate, not a ready home.",
        "After confirmation, write `state: pending` with the candidate's `thread_id` while preserving the evidence and approval values, then enter the common readiness sequence.",
        "New, recovered, and adopted tasks all use the same title-once, pin-once, re-list verification sequence before any `ready` write.",
    ),
    "stored thread recovery evidence": (
        "For a pending record with `thread_id`, first resolve that exact stored ID with `list_threads` and `read_thread` and require the exact saved `project_id`; then choose recovery proof from the record's creation path.",
        "For an adopted pending task, the exact canonical title is the recovery proof; do not require the recovery marker because the task may predate Design Arc.",
        "For a newly created pending task whose ready result supplied and stored `thread_id`, the exact recorded recovery marker in its initial prompt is the recovery proof, so the canonical title need not exist yet.",
        "If the exact stored ID does not resolve, the project identity mismatches, or neither allowed recovery proof matches, keep `state: pending`, report the stale or mismatched identity, and require explicit abandonment; never create a replacement automatically.",
        "Use `pending_since` plus recovery-marker candidate scanning only when a pending record has no `thread_id`.",
    ),
    "single ready mutation sequence": (
        "Call `set_thread_title` once, then call `set_thread_pinned` once, then call `list_threads` again and verify the canonical title, resolved project identity, and pinned state.",
        "Only after that verification, write `state: ready` with the verified `thread_id`.",
        "Do not mutate title or pin after verification.",
    ),
}

PROJECT_HOME_MUTATION_SEQUENCE = (
    "Write `state: pending` before calling `create_thread`.",
    "Call `create_thread` once.",
    "Call `set_thread_title` once",
    "call `set_thread_pinned` once",
    "call `list_threads` again and verify",
    "Only after that verification, write `state: ready`",
)

PROJECT_HOME_ADOPTION_SEQUENCE = (
    "An existing exact title-and-project match is an adoption candidate, not a ready home.",
    "After confirmation, write `state: pending` with the candidate's `thread_id`",
    "For a new, adopted, or exactly recovered task",
    "Call `set_thread_title` once",
    "call `set_thread_pinned` once",
    "call `list_threads` again and verify",
    "Only after that verification, write `state: ready`",
)

PROJECT_HOME_STORED_THREAD_RECOVERY_SEQUENCE = (
    "For a pending record with `thread_id`, first resolve that exact stored ID",
    "For an adopted pending task, the exact canonical title is the recovery proof",
    "For a newly created pending task whose ready result supplied and stored `thread_id`",
    "If the exact stored ID does not resolve, the project identity mismatches, or neither allowed recovery proof matches",
    "For a new, adopted, or exactly recovered task",
    "Call `set_thread_title` once",
    "call `set_thread_pinned` once",
    "call `list_threads` again and verify",
)

FORBIDDEN_PROJECT_HOME_PATTERNS = {
    "pending guard bypass": re.compile(
        r"(?:may|must|should)\s+(?:ignore|bypass).{0,100}(?:pending|ready).{0,100}(?:create|retry)",
        re.IGNORECASE | re.DOTALL,
    ),
    "silent home-state clearing": re.compile(
        r"(?:(?<!never )silently|without (?:explicit )?confirmation).{0,100}(?:clear|remove|delete).{0,100}(?:pending|ready|home record)",
        re.IGNORECASE | re.DOTALL,
    ),
    "ready before verification": re.compile(
        r"(?:mark|write|set).{0,60}(?:state:\s*)?ready.{0,120}before.{0,120}(?:verify|verification)",
        re.IGNORECASE | re.DOTALL,
    ),
    "mutation after verification": re.compile(
        r"after verification.{0,120}(?:call|run).{0,80}(?:set_thread_title|set_thread_pinned)",
        re.IGNORECASE | re.DOTALL,
    ),
    "direct ready adoption": re.compile(
        r"(?:adopt|reuse).{0,120}(?:by|directly|immediately).{0,80}(?:writ(?:e|ing)|mark|set).{0,60}(?:state:\s*)?`?ready`?",
        re.IGNORECASE | re.DOTALL,
    ),
    "adoption readiness bypass": re.compile(
        r"adopt(?:ed|ion)?.{0,120}(?:skip|bypass).{0,120}(?:pending|pin|list_threads|verification)",
        re.IGNORECASE | re.DOTALL,
    ),
    "absent direct to ready": re.compile(
        r"absent\s*(?:→|->|to)\s*ready",
        re.IGNORECASE,
    ),
    "adopted thread marker requirement": re.compile(
        r"adopted pending task.{0,180}(?<!do not )require (?:the )?(?:recorded )?recovery marker",
        re.IGNORECASE | re.DOTALL,
    ),
    "created thread title requirement": re.compile(
        r"newly created pending task.{0,220}(?:must|should|may only).{0,100}(?:canonical title|title match)",
        re.IGNORECASE | re.DOTALL,
    ),
    "created thread marker bypass": re.compile(
        r"newly created pending task.{0,220}(?:need not|does not need to|without).{0,100}(?:recovery marker|marker)",
        re.IGNORECASE | re.DOTALL,
    ),
    "stored thread automatic replacement": re.compile(
        r"(?:(?:missing|mismatched|unresolved).{0,160}(?:stored )?`?thread_id`?|(?:stored )?`?thread_id`?.{0,80}(?:is )?(?:missing|mismatched|unresolved)).{0,160}(?:may|must|should).{0,80}(?:create|replace)",
        re.IGNORECASE | re.DOTALL,
    ),
}


RENDER_REPAIR_HEADING = "### Repair visual drift before the Visual Proposal Gate"

ASSET_FIDELITY_HEADING = "### Bind the selected design to its production asset set"

ASSET_FIDELITY_CONTRACTS = {
    "case 01 platform baseline": (
        "The active AI coding platform must create a baseline design and a corresponding platform production asset set before design selection.",
    ),
    "case 02 Stitch set preservation": (
        "When Stitch is invoked, preserve its returned design and exported Stitch production asset set as a separate provenance-bound set; never overwrite either set with the other.",
    ),
    "case 03 selected-design binding": (
        "Record the selected design as `platform`, `stitch`, or `hybrid` and bind it to the matching asset set before implementation handoff.",
    ),
    "case 04 implementation integration": (
        "After separate implementation authorization, require the built application to import, reference, and render every required asset from the selected asset set.",
    ),
    "case 05 platform-selection isolation": (
        "A `platform` selection requires platform-generated assets and rejects every Stitch asset.",
    ),
    "case 06 Stitch-selection isolation": (
        "A `stitch` selection requires exported Stitch assets and rejects platform-generated substitutes.",
    ),
    "case 07 explicit hybrid approval": (
        "`Both` creates comparable proposals, not permission to mix their assets; mixing is allowed only after the user explicitly approves a `hybrid` design and identifies which screens, elements, and assets come from each set.",
    ),
    "case 08 blocking failures": (
        "Block implementation completion when any required selected asset is missing, unused, broken, unavailable, substituted, or absent from the running application.",
    ),
    "case 09 semantic UI": (
        "Keep controls, labels, navigation, state, status, focus behavior, and accessibility as semantic HTML or native UI; never flatten them into raster or vector artwork.",
    ),
    "case 10 raster capability block": (
        "When a required asset is raster and the active AI coding platform lacks native image-generation capability, record it as blocked and stop before design completion or implementation handoff; HTML/CSS, SVG, placeholders, and invented substitutes do not satisfy it.",
    ),
    "case 11 source and rendered proof": (
        "Return `matches approved proposal` only after both source integration and rendered fidelity pass: verify exact selected-asset imports and references, then inspect the running application at desktop and mobile viewports for correct loading and visual fidelity.",
    ),
}

RENDER_REPAIR_CONTRACTS = {
    "proposal-wide three-round bound": (
        "Use one initial visual proposal followed by at most three batched correction rounds for the entire proposal.",
        "The initial proposal is not a correction round, so the maximum is four rendered proposals.",
    ),
    "conformance matrix": (
        "Before assigning a visual verdict, create a conformance matrix for every material screen and state.",
        "Each row records the screen or state identifier; approved requirement and provenance; observed render evidence; classification; exact correction or next action; and inspected render identifier.",
    ),
    "classification boundary": (
        "Classify every mismatch as `match`, `repairable drift`, `direction decision required`, or `runtime proof`.",
        "Correct `repairable drift` automatically without asking the user because it does not change the approved direction.",
        "Stop before correction when a direction decision or new external authorization is required.",
        "Carry `runtime proof` forward as unverified implementation evidence; do not retry the renderer or claim the prototype proves it.",
    ),
    "inspection integrity": (
        "A correction note, provider status, or command success is not proof of correction; only inspection of the newly generated render can change a mismatch to `match`.",
        "After every correction round, inspect the complete resulting proposal again, including previously matching requirements that may have regressed.",
    ),
    "correction request integrity": (
        "Each correction request identifies the source render and affected screen/state IDs; states the observed mismatch and exact approved requirement; changes only `repairable drift`; preserves already matching requirements and the approved direction; requests a complete enough result to re-inspect affected and potentially regressed states; and records the new render or screen identifiers returned by the active renderer.",
        "Add newly introduced drift to the next batched round.",
    ),
    "bounded convergence": (
        "Stop early only when two consecutive corrected proposals show no improvement, two consecutive corrected proposals oscillate by fixing one requirement while breaking another, access becomes unavailable, the next correction changes direction, or new authorization is required.",
        "After the third unsuccessful correction round, stop and assign `meets with corrections` or `does not meet` from the remaining mismatch scope.",
        "Use `meets with corrections` only when unresolved bounded mismatches remain and the approved direction is still recognizable.",
        "Use `does not meet` when the proposal materially contradicts or fails to represent the approved direction.",
    ),
    "verdict integrity": (
        "Assign `meets direction` only after the most recent complete proposal is inspected and every renderer-expressible requirement matches.",
        "Guided and Follow recommendation perform the repair loop before stopping at the Visual Proposal Gate.",
        "After an unresolved verdict in Guided or Follow recommendation, offer the user choices to revise the direction, accept a clearly labeled product exception where allowed, or stop; an exception cannot change the verdict to `meets direction` or waive a current first-party platform or accessibility requirement.",
        "Fully automatic performs the same repair loop and continues past the Visual Proposal Gate only on `meets direction`.",
    ),
    "repair record": (
        "Record the initial proposal identifiers; each conformance matrix; correction round number; batched correction request and provenance; fixed, remaining, and newly introduced mismatches; stop reason; final visual verdict; and remaining runtime proof.",
    ),
}


def markdown_section(text: str, heading: str, next_prefix: str) -> str | None:
    start = text.find(heading)
    if start < 0:
        return None
    end = text.find(f"\n{next_prefix}", start + len(heading))
    return text[start:] if end < 0 else text[start:end]


def is_ordered(text: str, fragments: tuple[str, ...]) -> bool:
    cursor = 0
    for fragment in fragments:
        position = text.find(fragment, cursor)
        if position < 0:
            return False
        cursor = position + len(fragment)
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check deterministic Design Arc workflow contracts."
    )
    parser.add_argument("--skill", type=Path, default=DEFAULT_SKILL)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = args.skill.read_text(encoding="utf-8")
    except OSError as error:
        print(f"FAIL: cannot read Design Arc instruction contract: {error}", file=sys.stderr)
        return 1

    failures = []
    for label, fragments in REQUIRED_CONTRACTS.items():
        if any(fragment not in text for fragment in fragments):
            failures.append(f"missing or reversed {label} contract")

    for label, fragments in MOTION_CONTRACT_CASES.items():
        if any(fragment not in text for fragment in fragments):
            failures.append(f"missing or reversed motion {label} contract")

    for label, fragments in GRAPH_CONTRACT_CASES.items():
        if any(fragment not in text for fragment in fragments):
            failures.append(f"missing or reversed graph {label} contract")

    asset_fidelity = markdown_section(text, ASSET_FIDELITY_HEADING, "### ")
    if asset_fidelity is None:
        failures.append("missing selected-design asset-fidelity section")
    else:
        for label, fragments in ASSET_FIDELITY_CONTRACTS.items():
            if any(fragment not in asset_fidelity for fragment in fragments):
                failures.append(
                    f"missing or reversed selected-design asset-fidelity {label} contract"
                )

    render_repair = markdown_section(text, RENDER_REPAIR_HEADING, "## ")
    if render_repair is None:
        failures.append("missing render-repair section")
    else:
        for label, fragments in RENDER_REPAIR_CONTRACTS.items():
            if any(fragment not in render_repair for fragment in fragments):
                failures.append(f"missing or reversed render-repair {label} contract")

    project_home = markdown_section(text, PROJECT_HOME_HEADING, "### ")
    if project_home is None:
        failures.append("missing Project home section")
    else:
        for label, fragments in REQUIRED_PROJECT_HOME_CONTRACTS.items():
            if any(fragment not in project_home for fragment in fragments):
                failures.append(f"missing or reversed {label} contract")

        mutation_section = markdown_section(
            project_home, PROJECT_HOME_MUTATION_HEADING, "#### "
        )
        if mutation_section is None or not is_ordered(
            mutation_section, PROJECT_HOME_MUTATION_SEQUENCE
        ):
            failures.append("missing or reversed project-home mutation sequence")
        elif not is_ordered(mutation_section, PROJECT_HOME_ADOPTION_SEQUENCE):
            failures.append("missing or reversed project-home adoption sequence")
        elif not is_ordered(
            mutation_section, PROJECT_HOME_STORED_THREAD_RECOVERY_SEQUENCE
        ):
            failures.append("missing or reversed stored-thread recovery sequence")
        elif any(
            mutation_section.count(f"`{tool_name}`") != 1
            for tool_name in ("set_thread_title", "set_thread_pinned")
        ):
            failures.append("project-home title or pin mutation is not singular")

        for label, pattern in FORBIDDEN_PROJECT_HOME_PATTERNS.items():
            if pattern.search(project_home):
                failures.append(f"contradictory {label} contract")

    if failures:
        for failure in failures:
            print(f"FAIL: Design Arc: {failure}", file=sys.stderr)
        return 1

    print("PASS: deterministic Design Arc instruction contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
