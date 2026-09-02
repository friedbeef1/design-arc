#!/usr/bin/env python3
"""Mutation and path-boundary tests for production repository hygiene."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from check_repository_hygiene import forbidden_reason  # noqa: E402


FORBIDDEN_PATHS = (
    ".superpowers/plans/internal.md",
    "docs/superpowers/plans/internal.md",
    "docs/handoffs/release.md",
    "docs/retrospectives/review.md",
    "docs/validation/runtime-report.md",
    "docs/release-drafts/1.5.4.md",
    "docs/openai-plugin-directory-submission.md",
    ".codex/design-arc.yaml",
    ".codex/design-arc/reviews/review-1.json",
    ".claude/design-arc-active-review.json",
    ".gemini/design-arc-review.md",
)

ALLOWED_PATHS = (
    "README.md",
    "docs/runtime-boundaries.md",
    "docs/trust-limitations-and-sources.md",
    "docs/migration-history.md",
    ".codex/config.toml",
    ".codex/another-product.yaml",
    ".claude/settings.json",
    ".gemini/config/settings.json",
    "shared/design-arc/methodology.md",
)


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def main() -> int:
    for path in FORBIDDEN_PATHS:
        if forbidden_reason(path) is None:
            raise SystemExit(f"FAIL: forbidden-path mutation was accepted: {path}")

    for path in ALLOWED_PATHS:
        reason = forbidden_reason(path)
        if reason is not None:
            raise SystemExit(f"FAIL: allowed production path was rejected: {path}: {reason}")

    checker = SCRIPT_DIR / "check_repository_hygiene.py"
    with tempfile.TemporaryDirectory(prefix="design-arc-hygiene-") as raw_temp:
        repo = Path(raw_temp)
        run("git", "init", "-q", cwd=repo)
        run("git", "config", "user.name", "Design Arc Test", cwd=repo)
        run("git", "config", "user.email", "design-arc-test@example.invalid", cwd=repo)

        (repo / "docs").mkdir()
        (repo / "docs" / "runtime-boundaries.md").write_text("# Runtime boundaries\n", encoding="utf-8")
        run("git", "add", "docs/runtime-boundaries.md", cwd=repo)

        clean = run(sys.executable, str(checker), "--repo-root", str(repo), cwd=repo, check=False)
        if clean.returncode != 0:
            raise SystemExit(f"FAIL: clean tracked-path fixture was rejected:\n{clean.stdout}")

        forbidden = repo / ".codex" / "design-arc.yaml"
        forbidden.parent.mkdir()
        forbidden.write_text("evidence_mode: guidelines\n", encoding="utf-8")
        run("git", "add", "-f", ".codex/design-arc.yaml", cwd=repo)

        mutated = run(sys.executable, str(checker), "--repo-root", str(repo), cwd=repo, check=False)
        if mutated.returncode == 0:
            raise SystemExit("FAIL: tracked Design Arc state mutation was accepted")
        if ".codex/design-arc.yaml" not in mutated.stdout:
            raise SystemExit(f"FAIL: hygiene mutation failed without naming the path:\n{mutated.stdout}")

    print("PASS: repository hygiene path boundaries and tracked-state mutation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
