# GitHub primary distribution

- Owner: James's FB Tech chat, branch `codex/github-primary-20261003`.
- Scope: make GitHub the primary project home and installation route in the README and related installation documentation; retain the Codex directory as an optional route.
- Out of scope: plugin behavior, versions, installed packages, and directory package updates.
- Base: `5783909`, refreshed from `origin/main` on 2026-10-03.
- Authorization: James requested the GitHub-first changes and then said “Go live.”
- Public landing page: https://bit.ly/m/designarc — published and verified with GitHub first.
- Expected files: README.md, docs/getting-started.md, docs/codex.md, docs/trust-limitations-and-sources.md, scripts/test-design-arc-docs.sh, this record.
- Resumed 2026-10-06: public base is unchanged; documentation assertions are being updated to enforce the approved GitHub-first order.
- Status: documentation candidate complete and reviewed; approved for documentation-only publication.
- QA: `scripts/test-design-arc-docs.sh` passed, including link/fragment checks and mutation checks; `git diff --check` passed. Full diff reviewed for scope and retained directory access.
- Validation limitation: `scripts/validate.sh` passes required-file and metadata checks, then stops because the local system `plugin-creator/scripts/validate_plugin.py` is unavailable. No plugin package, behavior, or version changes are included; this documentation-only release relies on the passing documentation suite, not a claim of full plugin validation.
- Remaining check: verify the remote commit and documentation checks in a fresh public clone after push.
- Blockers: none for the documentation-only update; full plugin validation remains unavailable in this environment.
