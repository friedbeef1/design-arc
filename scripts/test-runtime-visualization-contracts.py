#!/usr/bin/env python3
"""Behavioral contracts for runtime-specific Design Arc visualization advice."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CODEX_SKILL = REPO_ROOT / "plugins/design-arc/skills/design-arc/SKILL.md"
CLAUDE_SKILL = REPO_ROOT / "claude-plugins/design-arc/skills/design-arc/SKILL.md"
ANTIGRAVITY_SKILL = REPO_ROOT / "skills/design-arc/SKILL.md"

ASSET_FIDELITY_CONTRACTS = (
    "The active AI coding platform must create a baseline design and a corresponding platform production asset set before design selection.",
    "When Stitch is invoked, preserve its returned design and exported Stitch production asset set as a separate provenance-bound set; never overwrite either set with the other.",
    "Record the selected design as `platform`, `stitch`, or `hybrid` and bind it to the matching asset set before implementation handoff.",
    "After separate implementation authorization, require the built application to import, reference, and render every required asset from the selected asset set.",
    "A `platform` selection requires platform-generated assets and rejects every Stitch asset.",
    "A `stitch` selection requires exported Stitch assets and rejects platform-generated substitutes.",
    "`Both` creates comparable proposals, not permission to mix their assets; mixing is allowed only after the user explicitly approves a `hybrid` design and identifies which screens, elements, and assets come from each set.",
    "Block implementation completion when any required selected asset is missing, unused, broken, unavailable, substituted, or absent from the running application.",
    "Keep controls, labels, navigation, state, status, focus behavior, and accessibility as semantic HTML or native UI; never flatten them into raster or vector artwork.",
    "When a required asset is raster and the active AI coding platform lacks native image-generation capability, record it as blocked and stop before design completion or implementation handoff; HTML/CSS, SVG, placeholders, and invented substitutes do not satisfy it.",
    "Return `matches approved proposal` only after both source integration and rendered fidelity pass: verify exact selected-asset imports and references, then inspect the running application at desktop and mobile viewports for correct loading and visual fidelity.",
)

BOTH_VISUALIZATION_CONTRACTS = (
    "When the user selects `Both`, start the AI coding platform visualization and the Stitch visualization concurrently from the same approved specification.",
    "Do not begin any correction round until both initial renders have finished successfully.",
    "After both initial renders finish, inspect each renderer independently against the same approved specification and record a separate conformance matrix and renderer-specific verdict before cross-comparing them.",
    "After the independent comparison, record the active correction scope as `platform`, `stitch`, or `both` from the user's explicit choice; selecting `Both` for initial generation does not select both renderers for correction.",
    "Correct only the renderer or renderers in the active correction scope, and preserve every unselected render and its independent inspection unchanged as comparison evidence.",
    "Run corrections concurrently only when the active correction scope is `both`; when it is `platform` or `stitch`, run only that renderer and do not wait for or modify the other.",
    "Treat `Both` as one paired proposal with one shared correction-round counter: at most three proposal-wide correction rounds total, not three rounds per renderer.",
    "For a `both` correction round, send renderer-specific correction batches concurrently, wait for both requested correction renders to finish, then reinspect each renderer independently before comparing the pair.",
    "If either initial renderer fails or becomes unavailable, stop the `Both` path and report the incomplete comparison; do not correct the completed renderer unless the user explicitly selects a single-renderer fallback.",
)

CODEX_STITCH_ONBOARDING_HEADING = "## Codex-only Stitch connection onboarding"

CODEX_STITCH_ONBOARDING_CONTRACTS = (
    "Run this connection check when the user selects Stitch or Both at the upfront renderer choice.",
    "The Live Codex plugin includes the Stitch MCP connection definition for `https://stitch.googleapis.com/mcp`; the user does not need to find or install a separate Stitch MCP.",
    "Inspect the Stitch tools actually available in the current Codex task; never infer a working connection from the bundled definition or server name alone.",
    "Verify a plausible Stitch connection with a read-only `list_projects` call or its exact equivalent.",
    "A successful call proves the connection even when it returns zero accessible projects; a failed or unauthorized call does not.",
    "Stitch provides an editable canvas for visual alternatives and sustained refinement.",
    "Then ask the user to enter their Stitch API key in Codex's secure credential prompt; do not ask them to find or install an MCP.",
    "Tell the user exactly where to create the key: open [Google Stitch](https://stitch.withgoogle.com/), select the Profile Picture, then **Stitch settings** → **API key** → **Create key**.",
    "The bundled connection sends the secure `STITCH_API_KEY` environment reference as the `X-Goog-Api-Key` header; it never contains a literal credential.",
    "Never ask the user to paste a Google API key into chat, and never read, display, log, write, commit, or store it in Design Arc state or project files.",
    "Ask the user only to complete the unavoidable key entry through Codex's secure credential interface.",
    "After setup, rediscover the Stitch tools and repeat the read-only project-list verification.",
    "After successful verification, resume at the pending renderer choice without repeating setup, Objective Confirmation, journey inspection, evidence gathering, or direction approval.",
    "If verification still fails, report the exact connection or authorization blocker and continue to offer the Codex visualization route; Stitch remains optional.",
)


def require(source: str, fragment: str, label: str) -> None:
    if fragment not in source:
        raise AssertionError(f"missing {label}: {fragment}")


def reject(source: str, fragment: str, label: str) -> None:
    if fragment in source:
        raise AssertionError(f"forbidden {label}: {fragment}")


def test_codex_visualization_contract() -> None:
    source = CODEX_SKILL.read_text(encoding="utf-8")
    require(source, "Create static screen images and complete journey boards directly in Codex by default.", "Codex default")
    require(source, "canvas-based editing, multiple visual alternatives, and sustained visual refinement", "Stitch benefits")
    require(source, "Stitch remains optional and separately authorized.", "optional authorization")
    require(source, "1. **Both Codex and Stitch — recommended**", "recommended combined choice")
    require(source, "2. **Codex only**", "Codex-only choice")
    require(source, "3. **Stitch only**", "Stitch-only choice")
    require(source, "Reply with `1`, `2`, or `3`.", "numeric visualization reply")
    require(
        source,
        "Both means create the Codex board and the Stitch visual workspace concurrently from the same approved journey.",
        "combined visualization behavior",
    )
    reject(source, "Stitch is mandatory", "mandatory Stitch")


def validate_codex_stitch_onboarding(source: str) -> None:
    require(source, CODEX_STITCH_ONBOARDING_HEADING, "Codex-only Stitch onboarding heading")
    for fragment in CODEX_STITCH_ONBOARDING_CONTRACTS:
        require(source, fragment, "Codex-only Stitch onboarding contract")


def test_codex_stitch_onboarding_contract() -> None:
    source = CODEX_SKILL.read_text(encoding="utf-8")
    validate_codex_stitch_onboarding(source)

    for fragment in CODEX_STITCH_ONBOARDING_CONTRACTS:
        mutated = source.replace(fragment, "", 1)
        try:
            validate_codex_stitch_onboarding(mutated)
        except AssertionError:
            continue
        raise AssertionError(f"Codex Stitch onboarding mutation survived: {fragment}")


def test_codex_stitch_onboarding_does_not_leak_to_alpha_adapters() -> None:
    for path in (CLAUDE_SKILL, ANTIGRAVITY_SKILL):
        reject(
            path.read_text(encoding="utf-8"),
            CODEX_STITCH_ONBOARDING_HEADING,
            f"Codex-only Stitch onboarding in {path}",
        )


def test_claude_visualization_contract() -> None:
    source = CLAUDE_SKILL.read_text(encoding="utf-8")
    require(source, "Never claim native image-generation capability in Claude Code.", "native-image disclaimer")
    require(source, "HTML/CSS, SVG, specifications, and lightweight static journey boards", "Claude outputs")
    require(source, "prepare a lightweight static journey board with HTML/CSS, SVG, or specifications", "Claude default route")
    require(source, "Immediately after the Direction Gate resolves and before either renderer starts", "upfront renderer timing")
    require(source, "1. **Both Claude Code and Stitch — recommended**", "recommended combined choice")
    require(source, "2. **Claude Code only**", "Claude-only choice")
    require(source, "3. **Stitch only**", "Stitch-only choice")
    require(source, "Reply with `1`, `2`, or `3`.", "numeric visualization reply")
    require(
        source,
        "Both means create the Claude Code board and the Stitch visual workspace concurrently from the same approved journey.",
        "combined visualization behavior",
    )
    require(source, "Never tell a Claude Code user to pass work to Codex unless the user explicitly requests a cross-platform handoff.", "no default Codex handoff")
    reject(source, "Generate one complete static journey board in Claude Code by default", "false native default")
    reject(source, "Claude Code can generate images natively", "native image-generation claim")
    reject(source, "Generate static screen images directly in Claude Code", "native screen-generation claim")
    reject(source, "pass work to Codex by default", "default Codex handoff")


def test_shared_stitch_validation_contract() -> None:
    for path in (CODEX_SKILL, CLAUDE_SKILL, ANTIGRAVITY_SKILL):
        source = path.read_text(encoding="utf-8")
        require(source, "Before using Stitch, prepare the complete evidence-grounded journey, requirements, and important-state inventory.", "Stitch preparation")
        require(source, "Stitch is a visualization tool, not an evidence authority.", "Stitch evidence boundary")
        require(source, "up to three correction rounds", "three-round active-host validation")


def test_shared_both_visualization_contract() -> None:
    for path in (CODEX_SKILL, CLAUDE_SKILL, ANTIGRAVITY_SKILL):
        source = path.read_text(encoding="utf-8")
        for fragment in BOTH_VISUALIZATION_CONTRACTS:
            require(source, fragment, f"Both visualization orchestration in {path}")


def test_shared_selected_asset_fidelity_contract() -> None:
    for path in (CODEX_SKILL, CLAUDE_SKILL, ANTIGRAVITY_SKILL):
        source = path.read_text(encoding="utf-8")
        for fragment in ASSET_FIDELITY_CONTRACTS:
            require(source, fragment, f"selected-asset fidelity in {path}")


def main() -> int:
    test_codex_visualization_contract()
    print("PASS: Codex visualization contract")
    test_codex_stitch_onboarding_contract()
    print("PASS: Codex-only Stitch onboarding contract and mutations")
    test_codex_stitch_onboarding_does_not_leak_to_alpha_adapters()
    print("PASS: Codex-only Stitch onboarding stays out of Alpha adapters")
    test_claude_visualization_contract()
    print("PASS: Claude visualization contract")
    test_shared_stitch_validation_contract()
    print("PASS: shared Stitch preparation and validation contract")
    test_shared_both_visualization_contract()
    print("PASS: shared Both visualization orchestration contract")
    test_shared_selected_asset_fidelity_contract()
    print("PASS: shared selected-design asset-fidelity contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
