#!/bin/sh
# Validate Design Arc's public product story and documentation boundaries.

set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(CDPATH= cd "$script_dir/.." && pwd)
task_temp_dir=$(mktemp -d "${TMPDIR:-/tmp}/design-arc-docs.XXXXXX")

cleanup() {
  [ -n "$task_temp_dir" ] && [ -d "$task_temp_dir" ] && rm -rf "$task_temp_dir"
}

fail() {
  printf '%s\n' "FAIL: $*" >&2
  exit 1
}

trap cleanup EXIT HUP INT TERM

require_text() {
  file=$1
  text=$2
  grep -F "$text" "$file" >/dev/null || fail "missing required text in ${file#"$repo_root/"}: $text"
}

forbid_text() {
  file=$1
  text=$2
  if grep -F "$text" "$file" >/dev/null
  then
    fail "forbidden text remains in ${file#"$repo_root/"}: $text"
  fi
}

copy_fixture() {
  destination=$1
  mkdir -p "$destination"
  (
    cd "$repo_root"
    tar --exclude=.git --exclude=.superpowers -cf - .
  ) | (
    cd "$destination"
    tar -xf -
  )
}

readme="$repo_root/README.md"
getting_started="$repo_root/docs/getting-started.md"
using_design_arc="$repo_root/docs/using-design-arc.md"
codex_edition="$repo_root/docs/codex.md"
claude_edition="$repo_root/docs/claude-code.md"
antigravity_edition="$repo_root/docs/antigravity.md"
advanced_controls="$repo_root/docs/advanced-controls.md"
evidence_methodology="$repo_root/docs/evidence-and-methodology.md"
upgrades_migration="$repo_root/docs/upgrades-and-migration.md"
migration_history="$repo_root/docs/migration-history.md"
trust_sources="$repo_root/docs/trust-limitations-and-sources.md"
privacy_policy="$repo_root/docs/privacy.md"
terms="$repo_root/docs/terms.md"
support="$repo_root/docs/support.md"
faq="$repo_root/docs/faq.md"
operating_layer="$repo_root/docs/codex-operating-layer.md"
runtime_boundaries="$repo_root/docs/runtime-boundaries.md"
prompts="$repo_root/examples/prompts.md"
motion_sources="$repo_root/docs/trusted-sources/motion.md"
trusted_source_library="$repo_root/docs/trusted-sources/README.md"
visualization_sources="$repo_root/docs/trusted-sources/visualization.md"
shared_navigation='[Home](../README.md) · [Getting started](getting-started.md) · [Using Design Arc](using-design-arc.md) · [Codex](codex.md) · [Claude Code](claude-code.md) · [Google Antigravity](antigravity.md) · [FAQ](faq.md) · [Runtime boundaries](runtime-boundaries.md) · [Advanced controls](advanced-controls.md) · [Evidence and methodology](evidence-and-methodology.md) · [Upgrades and migration](upgrades-and-migration.md) · [Migration history](migration-history.md) · [Trust and sources](trust-limitations-and-sources.md)'
historical_navigation='[Home](../README.md) · [Getting started](getting-started.md) · [Using Design Arc](using-design-arc.md) · [Codex](codex.md) · [Claude Code](claude-code.md) · [FAQ](faq.md) · [Runtime boundaries](runtime-boundaries.md) · [Advanced controls](advanced-controls.md) · [Evidence and methodology](evidence-and-methodology.md) · [Upgrades and migration](upgrades-and-migration.md) · [Migration history](migration-history.md) · [Trust and sources](trust-limitations-and-sources.md)'

for file in "$readme" "$getting_started" "$using_design_arc" "$codex_edition" "$claude_edition" "$antigravity_edition" "$faq" "$advanced_controls" "$evidence_methodology" "$upgrades_migration" "$migration_history" "$trust_sources" "$privacy_policy" "$terms" "$support" "$operating_layer" "$runtime_boundaries" "$prompts" "$motion_sources" "$trusted_source_library" "$visualization_sources"
do
  [ -f "$file" ] || fail "missing required documentation: ${file#"$repo_root/"}"
done

require_text "$readme" '[FAQ](docs/faq.md)'
require_text "$readme" 'One Design Arc, available for Codex (live), Claude Code (alpha), and Google Antigravity (alpha).'
require_text "$readme" 'Design Arc works in three AI coding platforms: Codex, Claude Code, and Google Antigravity.'
require_text "$readme" '[Design Arc for Codex](docs/codex.md)'
require_text "$readme" '[Design Arc for Claude Code](docs/claude-code.md)'
require_text "$readme" '[Design Arc for Google Antigravity](docs/antigravity.md)'
require_text "$readme" '[Privacy](docs/privacy.md)'
require_text "$readme" '[Terms](docs/terms.md)'
require_text "$readme" '[Support](docs/support.md)'
require_text "$privacy_policy" 'Design Arc does not operate a developer-controlled backend'
require_text "$privacy_policy" 'External services remain separately authorized'
require_text "$terms" 'Design Arc is a design-review aid, not proof of legal, accessibility, security, implementation, or release compliance.'
require_text "$support" 'https://github.com/friedbeef1/design-arc/issues'

for file in "$readme" "$repo_root"/docs/*.md "$repo_root"/docs/trusted-sources/*.md
do
  if grep -Ei 'active[ -]host' "$file" >/dev/null
  then
    fail "deprecated public term remains in ${file#"$repo_root/"}: active host"
  fi
  if grep -i 'host-specific' "$file" >/dev/null
  then
    fail "deprecated public term remains in ${file#"$repo_root/"}: host-specific"
  fi
done
directory_listing='https://chatgpt.com/plugins/plugins_6a82ffefdc88819191f5eaab4eaf116b'
require_text "$readme" "$directory_listing"
require_text "$getting_started" "$directory_listing"
require_text "$codex_edition" "$directory_listing"
require_text "$trust_sources" "$directory_listing"
require_text "$readme" 'Install the Live Codex edition from the OpenAI Plugin Directory'
require_text "$getting_started" 'Install the Live Codex edition from the OpenAI Plugin Directory'
require_text "$codex_edition" 'Install the Live Codex edition from the OpenAI Plugin Directory'
forbid_text "$trust_sources" 'Until an approved listing is actually published'
forbid_text "$trust_sources" 'preparing or submitting a candidate does not mean OpenAI has approved or listed it'
require_text "$readme" '| [**Codex**](docs/codex.md) | **Live** |'
require_text "$readme" '| [**Claude Code**](docs/claude-code.md) | **Alpha** |'
require_text "$readme" '| [**Google Antigravity**](docs/antigravity.md) | **Alpha** |'
require_text "$getting_started" 'Codex is the **Live** edition. Claude Code and Google Antigravity are **Alpha** editions.'
require_text "$codex_edition" '# Design Arc for Codex — Live'
require_text "$claude_edition" '# Design Arc for Claude Code — Alpha'
require_text "$antigravity_edition" '# Design Arc for Google Antigravity — Alpha'
require_text "$codex_edition" '## What stays the same'
require_text "$codex_edition" 'pinned project home'
require_text "$claude_edition" '## What stays the same'
require_text "$claude_edition" 'Claude Code does not create a Codex project home.'
require_text "$antigravity_edition" '# Design Arc for Google Antigravity'
require_text "$antigravity_edition" 'Google Antigravity Desktop does not require Antigravity CLI to use Design Arc.'
require_text "$antigravity_edition" 'Install Design Arc globally from https://github.com/friedbeef1/design-arc'
require_text "$antigravity_edition" '`~/.gemini/config/skills/design-arc/`'
require_text "$antigravity_edition" 'Because the Antigravity package is skills-only'
require_text "$antigravity_edition" '## Optional CLI installation'
require_text "$antigravity_edition" 'agy plugin install https://github.com/friedbeef1/design-arc'
require_text "$antigravity_edition" '`/design-arc`'
require_text "$antigravity_edition" 'Desktop, IDE, and CLI surfaces when that surface has loaded the Design Arc skill'
require_text "$antigravity_edition" 'The repository test suite validates the packaged Antigravity adapter and its written contracts.'
require_text "$antigravity_edition" 'it does not prove the optional `agy plugin install` route or `/design-arc` loading in CLI.'
require_text "$antigravity_edition" 'Google Antigravity owns `.gemini/design-arc.yaml`, `.gemini/design-arc-active-review.json`, and review artifacts under `.gemini/design-arc/reviews/`.'
require_text "$antigravity_edition" 'Never import, merge, migrate, resume, or continue an active review across runtimes.'
require_text "$antigravity_edition" 'Only when `.gemini/design-arc.yaml` is absent can Design Arc offer a one-time, explicitly confirmed preference import from Codex or Claude Code.'
require_text "$antigravity_edition" 'If both source preferences exist, choose exactly one validated source; Design Arc never merges them.'
require_text "$antigravity_edition" 'lightweight static journey board with HTML/CSS, SVG, or specifications'
require_text "$antigravity_edition" 'does not claim native image generation'
require_text "$antigravity_edition" 'Stitch remains optional and separately authorized.'
require_text "$antigravity_edition" 'The extension installation does not authorize benchmark, browser, visualization, MCP, provider, or product access.'
require_text "$antigravity_edition" 'Use a supported Google Antigravity extension update route.'
python3 - "$antigravity_edition" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
desktop = text.find("## Install in Antigravity Desktop")
cli = text.find("## Optional CLI installation")
if desktop == -1 or cli == -1 or desktop > cli:
    raise SystemExit("FAIL: Antigravity Desktop installation must appear before optional CLI installation")
PY
require_text "$faq" '**What is a Codex project home?**'
require_text "$faq" '**Are the Codex, Claude Code, and Google Antigravity editions different products?**'
require_text "$faq" 'An optional pinned Codex task that gives one product a visible place to return to Design Arc later.'
require_text "$faq" '[Returning later in Codex](codex.md#returning-later)'
require_text "$faq" '[Returning later in Claude Code](claude-code.md#returning-later)'
for forbidden_shared_lifecycle in \
  'A project home is an optional pinned Codex task for one particular product.' \
  'The Design Arc plugin is installed once on your laptop; each participating product may have one separate project home. Claude Code does not use project homes. It uses an optional project reminder instead.' \
  'Codex users can also return through their pinned project home.'
do
  forbid_text "$faq" "$forbidden_shared_lifecycle"
done

python3 - "$readme" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
line_count = len(text.splitlines())
if not 80 <= line_count <= 140:
    raise SystemExit(f"FAIL: README must contain 80-140 lines; found {line_count}")

opening_description = "Design Arc audits the real journey, checks decisions against current first-party platform guidance and inspected real-product journeys, recommends the strongest path, and designs every important state before implementation begins."
action_section = """### See Design Arc in action
See how Design Arc turns vague feedback into an evidence-backed direction—watch the demo or browse the introduction deck.

| Product walkthrough | Introduction deck |
| --- | --- |
| [![Design Arc product demo thumbnail — opens YouTube](https://img.youtube.com/vi/Zt7ba_lngxk/maxresdefault.jpg)](https://youtu.be/Zt7ba_lngxk) | [![Design Arc introduction deck cover — opens presentation](https://docs.google.com/presentation/d/1EG5vrPC5UqAkNAr9jce0lvZz1Jq5oI4AqAbPVivG2sU/export/png?id=1EG5vrPC5UqAkNAr9jce0lvZz1Jq5oI4AqAbPVivG2sU&pageid=g3fab99837d7_0_185)](https://docs.google.com/presentation/d/1EG5vrPC5UqAkNAr9jce0lvZz1Jq5oI4AqAbPVivG2sU/preview) |
| [Watch on YouTube](https://youtu.be/Zt7ba_lngxk) | [Open presentation](https://docs.google.com/presentation/d/1EG5vrPC5UqAkNAr9jce0lvZz1Jq5oI4AqAbPVivG2sU/preview) |"""
if action_section not in text:
    raise SystemExit("FAIL: README action section must retain the ordered two-card demo and introduction-deck resources")

action_position = text.index(action_section)
description_end = text.index(opening_description) + len(opening_description)
documentation_position = text.index("## Documentation")
if action_position != description_end + 1:
    raise SystemExit("FAIL: README action section must immediately follow the opening product description")
if action_position > documentation_position:
    raise SystemExit("FAIL: README action section must appear before Documentation")

directory_instruction = "[Install the Live Codex edition from the OpenAI Plugin Directory](https://chatgpt.com/plugins/plugins_6a82ffefdc88819191f5eaab4eaf116b)"
fallback_instruction = "ask Codex to install the Design Arc plugin from https://github.com/friedbeef1/design-arc"
if directory_instruction not in text:
    raise SystemExit("FAIL: README is missing the primary OpenAI Plugin Directory instruction")
if fallback_instruction not in text:
    raise SystemExit("FAIL: README is missing the GitHub fallback installation instruction")
if text.find(directory_instruction) > text.find(fallback_instruction):
    raise SystemExit("FAIL: README must present the OpenAI Plugin Directory before the GitHub fallback")

for forbidden_text in ("```sh", "codex plugin", "skills registry", "Python", "Saved preferences and migration", "If Codex says"):
    if forbidden_text in text:
        raise SystemExit(f"FAIL: README retains forbidden advanced-installation content: {forbidden_text}")
PY

python3 - "$repo_root" <<'PY'
from pathlib import Path
import re
import sys
from urllib.parse import unquote

repository_root = Path(sys.argv[1]).resolve()
documentation_pages = sorted(
    [repository_root / "README.md"]
    + list((repository_root / "docs").glob("*.md"))
    + list((repository_root / "docs" / "trusted-sources").glob("*.md"))
    + [repository_root / "examples" / "prompts.md"]
)


def heading_fragments(page):
    fragments = set()
    occurrences = {}
    for line in page.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        heading = re.sub(r"<[^>]+>", "", match.group(1))
        heading = re.sub(r"[`*_~]", "", heading).strip().lower()
        slug = "".join(character for character in heading if character.isalnum() or character in " _-")
        slug = re.sub(r"\s+", "-", slug)
        occurrence = occurrences.get(slug, 0)
        occurrences[slug] = occurrence + 1
        fragments.add(slug if occurrence == 0 else f"{slug}-{occurrence}")
    return fragments

for source in documentation_pages:
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", source.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        relative_path, separator, fragment = target.partition("#")
        resolved = (source.parent / relative_path).resolve() if relative_path else source.resolve()
        try:
            resolved.relative_to(repository_root)
        except ValueError:
            raise SystemExit(f"FAIL: relative link escapes repository in {source}: {target}")
        if not resolved.exists():
            raise SystemExit(f"FAIL: broken relative link in {source}: {target}")
        if separator and resolved.suffix.lower() == ".md" and unquote(fragment) not in heading_fragments(resolved):
            raise SystemExit(f"FAIL: broken Markdown fragment in {source}: {target}")

print(f"PASS: repository-relative Markdown links and fragments resolve across {len(documentation_pages)} public pages")
PY

require_text "$readme" '# Design Arc'
require_text "$readme" 'Product feedback is often vague, redesign discussions become subjective, and teams approve attractive screens without knowing whether the complete journey works.'
require_text "$readme" 'Move from uncertain product feedback to a complete design direction grounded in credible sources.'
require_text "$readme" 'Design Arc audits the real journey, checks decisions against current first-party platform guidance and inspected real-product journeys, recommends the strongest path, and designs every important state before implementation begins.'
require_text "$readme" '## You need Design Arc if…'
require_text "$readme" '## What Design Arc produces'
require_text "$readme" '## One product, three platform editions'
require_text "$readme" '| Use | Release status | Choose it when | Start Design Arc |'
require_text "$readme" 'The product and workflow are shared. Start with Design Arc, then use the runtime page for Codex, Claude Code, or Google Antigravity when installation, saved state, return paths, or visual capabilities differ.'
require_text "$readme" '[Codex runtime details](docs/codex.md)'
require_text "$readme" '[Claude Code runtime details](docs/claude-code.md)'
require_text "$readme" '[Runtime boundaries](docs/runtime-boundaries.md)'
require_text "$readme" '## The workflow'
require_text "$readme" '## Documentation'
require_text "$readme" '[Getting started](docs/getting-started.md)'
require_text "$readme" '[Using Design Arc](docs/using-design-arc.md)'
require_text "$readme" '[Advanced controls](docs/advanced-controls.md)'
require_text "$readme" '[Evidence and methodology](docs/evidence-and-methodology.md)'
require_text "$readme" '[Upgrades and migration](docs/upgrades-and-migration.md)'
require_text "$readme" '[Migration history](docs/migration-history.md)'
require_text "$readme" '[Trust and sources](docs/trust-limitations-and-sources.md)'
require_text "$readme" '## Install'
require_text "$readme" '**Ask Claude Code:** Add the Design Arc marketplace from'
require_text "$readme" '## Start a review'
require_text "$readme" 'Use Design Arc to help me make our onboarding less confusing.'
require_text "$readme" 'You do not need to remember a command.'
require_text "$readme" '## Trust'
require_text "$readme" 'Design Arc does not silently redesign, implement, or deploy your product. You choose the objective, evidence approach, and approval behavior.'
require_text "$readme" '## License'
require_text "$readme" '[MIT License](LICENSE)'

require_text "$codex_edition" '## State'
require_text "$codex_edition" 'Codex owns `.codex/design-arc.yaml`, its review records, and its graph records.'
require_text "$codex_edition" 'The optional pinned project home remains a Codex-owned return path.'
require_text "$codex_edition" '## Upgrade'
require_text "$codex_edition" 'Ask Codex to upgrade Design Arc safely through its configured marketplace.'
require_text "$codex_edition" 'The upgrade preserves `.codex/design-arc.yaml`, the optional pinned project home, review records, graph records, product files, and active tasks byte-for-byte.'
require_text "$codex_edition" 'After verifying the installed version and preservation result, start the next review in a clean Codex task.'
require_text "$codex_edition" 'Codex does not synchronize, merge, import, or mutate Claude Code state.'

require_text "$claude_edition" '## State'
require_text "$claude_edition" 'Claude Code owns `.claude/design-arc.yaml`, its review records, and its graph records.'
require_text "$claude_edition" 'The optional approved `CLAUDE.md` reminder remains a Claude Code-owned return path.'
require_text "$claude_edition" '## Import portable preferences from Codex'
require_text "$claude_edition" 'Claude Code offers this one-time import only when `.claude/design-arc.yaml` is absent.'
require_text "$claude_edition" 'After explicit confirmation, only evidence mode, a valid benchmark provider, approval mode, and graph assistance are copied.'
require_text "$claude_edition" 'Codex bytes, homes, active reviews, review records, and graph records are not merged or changed.'
require_text "$claude_edition" '## Upgrade'
require_text "$claude_edition" 'claude plugin update design-arc@design-arc-marketplace'
require_text "$claude_edition" 'The upgrade preserves `.claude/design-arc.yaml`, the approved `CLAUDE.md` reminder, review records, graph records, product files, and active sessions byte-for-byte.'
require_text "$claude_edition" 'After verifying the installed version and source, start the next review in a clean Claude Code session.'
require_text "$claude_edition" 'The upgrade does not import preferences or synchronize, merge, or mutate Codex state.'

forbid_text "$migration_history" '## Historical Claude preference import'
forbid_text "$migration_history" 'Claude Code may propose importing portable values from `.codex/design-arc.yaml`'

for file in "$getting_started" "$using_design_arc" "$codex_edition" "$claude_edition" "$antigravity_edition" "$faq" "$advanced_controls" "$evidence_methodology" "$upgrades_migration" "$trust_sources" "$runtime_boundaries"
do
  require_text "$file" "$shared_navigation"
done
require_text "$migration_history" "$historical_navigation"

require_text "$getting_started" '# Getting started'
require_text "$getting_started" 'How do I install Design Arc and begin my first review?'
require_text "$getting_started" '## Install once'
require_text "$getting_started" '## Start by describing the problem'
require_text "$getting_started" 'Use Design Arc to help me improve our onboarding.'
require_text "$getting_started" 'Design Arc guides setup in plain language the first time a project uses it.'
require_text "$getting_started" '## Install in Claude Code'
require_text "$getting_started" '## Install in Google Antigravity'
require_text "$getting_started" 'Install Design Arc globally from https://github.com/friedbeef1/design-arc'
require_text "$getting_started" 'You do not need Antigravity CLI for Desktop use.'
require_text "$getting_started" 'Choose the runtime page for the AI coding platform for installation, saved state, and returning later.'
require_text "$getting_started" '[Design Arc for Codex](codex.md)'
require_text "$getting_started" '[Design Arc for Claude Code](claude-code.md)'
require_text "$getting_started" '[Design Arc for Google Antigravity](antigravity.md)'
require_text "$getting_started" 'No Python knowledge is required.'
require_text "$getting_started" 'Technical commands and troubleshooting live in [Advanced controls](advanced-controls.md).'
require_text "$getting_started" 'Next: [Using Design Arc](using-design-arc.md).'

require_text "$faq" '# Frequently asked questions'
require_text "$faq" 'Use the short answers below, then follow the relevant guide when you want the full explanation.'
require_text "$faq" '## Getting started'
require_text "$faq" '## Evidence and recommendations'
require_text "$faq" '## Approvals and automation'
require_text "$faq" '## Screens, visual proposals, and Stitch'
require_text "$faq" '## Projects and AI coding platforms'
require_text "$faq" '## Installation, upgrades, privacy, and support'
require_text "$faq" '| Question | Short answer | Full explanation |'
require_text "$faq" '**Do I need to remember a Design Arc command?**'
require_text "$faq" '**What is a Codex project home?**'
require_text "$faq" '**Is Mobbin required?**'
require_text "$faq" '**Is Google Stitch required?**'
require_text "$faq" '**What happens after three unsuccessful correction rounds?**'
require_text "$faq" '**Do Codex, Claude Code, and Google Antigravity share project state?**'
require_text "$faq" '**Will an upgrade disturb existing projects?**'

python3 - "$faq" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
question_rows = [line for line in text.splitlines() if line.startswith("| **")]
if len(question_rows) < 24:
    raise SystemExit(f"FAIL: FAQ has only {len(question_rows)} question rows; expected at least 24")
for row in question_rows:
    if "](" not in row:
        raise SystemExit(f"FAIL: FAQ question lacks a detailed-page link: {row}")
print(f"PASS: FAQ routes {len(question_rows)} practical questions to detailed pages")
PY

require_text "$using_design_arc" '# Using Design Arc'
require_text "$using_design_arc" 'Describe the product outcome you want in ordinary language.'
require_text "$using_design_arc" 'Commands are optional shortcuts, not required knowledge.'
require_text "$using_design_arc" 'Codex, Claude Code, and Google Antigravity never merge, migrate, resume, or continue an active review across runtimes.'
require_text "$using_design_arc" 'If your AI coding platform selects Design Arc for a suitable request that did not invoke it directly, it asks for permission before beginning.'
require_text "$using_design_arc" 'Automatic skill selection is not guaranteed'
require_text "$using_design_arc" 'ask for Design Arc by name when certainty matters.'
require_text "$using_design_arc" 'Design Arc does not run continuously or silently in every task.'
require_text "$using_design_arc" 'How do I use Design Arc after installation?'
require_text "$using_design_arc" 'Codex, Claude Code, or Google Antigravity may offer Design Arc for requests such as:'
forbid_text "$using_design_arc" 'Examples of requests for which Codex or Claude Code may offer Design Arc include:'
require_text "$using_design_arc" 'Runtime-specific installation, invocation, saved state, returning later, visual capabilities, and upgrades belong to the [Codex runtime](codex.md), [Claude Code runtime](claude-code.md), and [Google Antigravity runtime](antigravity.md) pages.'
require_text "$using_design_arc" '[Runtime boundaries](runtime-boundaries.md)'
require_text "$using_design_arc" 'Help me make our onboarding less confusing.'
require_text "$using_design_arc" 'Audit how customers complete checkout and propose a better complete journey.'
require_text "$using_design_arc" 'Redesign account recovery so people can get back in without weakening security.'
require_text "$using_design_arc" '## Choosing your AI coding platform or Stitch for the screens'
require_text "$using_design_arc" 'Design Arc generates one complete static journey board in your AI coding platform by default.'
require_text "$using_design_arc" 'It does not build disposable application logic merely to visualize the proposal.'
require_text "$using_design_arc" 'Stitch is optional and Design Arc recommends it when any one genuine canvas trigger occurs.'
require_text "$using_design_arc" 'A Stitch recommendation is advisory and never transfers the proposal automatically.'
require_text "$using_design_arc" 'You can stay in your AI coding platform.'
require_text "$using_design_arc" 'If you say not to recommend Stitch again for this review, Design Arc suppresses every further recommendation for that review.'
require_text "$using_design_arc" 'When you choose both, Design Arc starts the AI coding platform board and Stitch workspace concurrently from the same approved specification.'
require_text "$using_design_arc" 'It waits for both initial renders before correcting either one.'
require_text "$using_design_arc" 'Each render is then checked independently against the approved specification before the pair is compared.'
require_text "$using_design_arc" 'Both share one limit of three proposal-wide correction rounds; they do not receive three rounds each.'
require_text "$faq" '**What happens when I choose Both?**'
require_text "$faq" 'The platform board and Stitch workspace start concurrently from the same approved specification. Design Arc waits for both, checks each independently, and uses one shared three-round correction limit.'
require_text "$using_design_arc" 'The same validation and correction rules apply whether your AI coding platform or Stitch renders the screens.'
require_text "$using_design_arc" 'Design Arc corrects straightforward visual drift before asking you to approve the visual proposal.'
require_text "$using_design_arc" 'The initial proposal may be followed by at most three correction rounds for the whole proposal.'
require_text "$using_design_arc" 'Each round batches every known repairable mismatch, generates a new proposal, and reinspects the complete result.'
require_text "$using_design_arc" 'If the proposal still does not match, Design Arc stops and flags every unresolved mismatch and the attempts already made.'
require_text "$using_design_arc" '| Approval mode | Objective | Visual Proposal Gate |'
require_text "$using_design_arc" 'Select evidence mode<br/>AI coding platform; You when a choice is required'
require_text "$using_design_arc" 'C -- "Guidelines only mode" --> C1'
require_text "$using_design_arc" 'Official Apple Human Interface Guidelines for Apple,'
require_text "$using_design_arc" 'Android and Material guidance for Android,'
require_text "$using_design_arc" 'or W3C guidance for web + AI coding platform'
require_text "$using_design_arc" 'C -- "Guidelines + Benchmarks mode" --> C2'
require_text "$using_design_arc" 'Mobbin journey benchmarks + applicable'
require_text "$using_design_arc" 'Google Stitch + AI coding platform'
require_text "$using_design_arc" 'Generated screens + AI coding platform'
require_text "$using_design_arc" 'Design Arc bundles no MCP server'
require_text "$using_design_arc" 'Google now provides an official Stitch MCP server and SDK'
require_text "$using_design_arc" 'only when it is separately installed, configured, and authorized'
require_text "$using_design_arc" 'name the exact configured MCP server or tool'
require_text "$using_design_arc" 'does not imply an official Mobbin MCP integration'
require_text "$using_design_arc" 'Design Arc does not silently redesign, implement, or deploy your product. You choose the objective, evidence approach, and approval behavior.'
require_text "$using_design_arc" 'Design Arc understands how requirements, evidence and screens affect one another, helping it make more precise corrections without surrendering approval control.'
require_text "$using_design_arc" 'Graph assistance is active by default for every new 0.3.0 review in both existing and new projects when no project or platform-local safety control turns it off.'
require_text "$using_design_arc" 'An active review remains exactly as it started; its next clean review gains the 0.3.0 assistance.'
require_text "$using_design_arc" 'Graph assistance adds no approval gate.'
require_text "$using_design_arc" 'Graph assistance is optional internal reasoning support.'
require_text "$using_design_arc" 'People who want to inspect or manage it can use the commands in [Advanced controls](advanced-controls.md).'
require_text "$using_design_arc" 'Next: [Evidence and methodology](evidence-and-methodology.md).'

python3 - "$using_design_arc" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
approval_controls = text.find("## Approval and trust controls")
graph_assistance = text.find("## Graph-assisted corrections")
if approval_controls == -1 or graph_assistance == -1:
    raise SystemExit("FAIL: shared usage page is missing required core or graph guidance")
if graph_assistance < approval_controls:
    raise SystemExit("FAIL: shared usage page must keep graph assistance after core approval guidance")
PY

require_text "$advanced_controls" '# Advanced controls'
require_text "$advanced_controls" 'You do not need these commands for normal Design Arc use.'
require_text "$advanced_controls" '## Google Antigravity controls'
require_text "$advanced_controls" 'Google Antigravity guarantees the `/design-arc` entry point; start there, then ask in ordinary language for the shared action you want.'
require_text "$advanced_controls" 'agy plugin install https://github.com/friedbeef1/design-arc'
for command in \
  '$design-arc setup' \
  '$design-arc home' \
  '$design-arc evidence benchmarks' \
  '$design-arc evidence guidelines' \
  '$design-arc mode guided' \
  '$design-arc mode follow-recommendation' \
  '$design-arc mode fully-automatic' \
  '$design-arc graph on' \
  '$design-arc graph off' \
  '/design-arc:design-arc graph on' \
  '/design-arc:design-arc graph off'
do
  require_text "$advanced_controls" "$command"
done

python3 - "$codex_edition" "$claude_edition" "$advanced_controls" "$prompts" <<'PY'
from pathlib import Path
import sys

codex = Path(sys.argv[1]).read_text(encoding="utf-8")
claude = Path(sys.argv[2]).read_text(encoding="utf-8")
controls = Path(sys.argv[3]).read_text(encoding="utf-8")
prompts = Path(sys.argv[4]).read_text(encoding="utf-8")

plain_starter = "Use Design Arc to help me improve our onboarding."
for name, text in (("Codex runtime page", codex), ("Claude Code runtime page", claude)):
    if plain_starter not in text:
        raise SystemExit(f"FAIL: {name} must lead with a plain-language starter")

command_pairs = (
    ("$design-arc", "/design-arc:design-arc"),
    ("$design-arc setup", "/design-arc:design-arc setup"),
    ("$design-arc upgrade", "/design-arc:design-arc upgrade"),
    ("$design-arc evidence benchmarks", "/design-arc:design-arc evidence benchmarks"),
    ("$design-arc evidence guidelines", "/design-arc:design-arc evidence guidelines"),
    ("$design-arc mode", "/design-arc:design-arc mode"),
    ("$design-arc mode guided", "/design-arc:design-arc mode guided"),
    ("$design-arc mode follow-recommendation", "/design-arc:design-arc mode follow-recommendation"),
    ("$design-arc mode fully-automatic", "/design-arc:design-arc mode fully-automatic"),
    ("$design-arc graph", "/design-arc:design-arc graph"),
    ("$design-arc graph on", "/design-arc:design-arc graph on"),
    ("$design-arc graph off", "/design-arc:design-arc graph off"),
    ("$design-arc graph explain", "/design-arc:design-arc graph explain"),
    ("$design-arc graph rebuild", "/design-arc:design-arc graph rebuild"),
    ("$design-arc graph clear", "/design-arc:design-arc graph clear"),
    ("$design-arc graph global off", "/design-arc:design-arc graph global off"),
    ("$design-arc graph global on", "/design-arc:design-arc graph global on"),
)
for codex_command, claude_command in command_pairs:
    if codex_command not in controls or claude_command not in controls:
        raise SystemExit(f"FAIL: advanced controls must pair {codex_command} with {claude_command}")

if "$design-arc home" not in controls or "/design-arc:design-arc home" in controls:
    raise SystemExit("FAIL: project-home control must remain an explicit Codex-only exception")
if "pinned project home" not in codex:
    raise SystemExit("FAIL: Codex runtime page must preserve the Codex-only project home")
if "`CLAUDE.md` reminder" not in claude:
    raise SystemExit("FAIL: Claude Code runtime page must preserve the Claude-only reminder")
if "Claude Code does not create a Codex project home." not in claude:
    raise SystemExit("FAIL: Claude Code runtime page must reject Codex project homes")
if "Static screen images and complete journey boards directly in Codex by default." not in codex:
    raise SystemExit("FAIL: Codex runtime page must retain its direct visualization capability")
if "does not claim native image generation" not in claude:
    raise SystemExit("FAIL: Claude Code runtime page must not claim native image generation")

required_matrix_rows = (
    "| Start a review | “Use Design Arc to help me improve our onboarding.” | `$design-arc` | `/design-arc:design-arc` |",
    "| Review setup | “Show this project’s Design Arc choices.” | `$design-arc setup` | `/design-arc:design-arc setup` |",
    "| Upgrade safely | “Upgrade Design Arc safely.” | `$design-arc upgrade` | `/design-arc:design-arc upgrade` |",
    "| Use Guidelines + Benchmarks | “Use authorized benchmarks and official guidance.” | `$design-arc evidence benchmarks` | `/design-arc:design-arc evidence benchmarks` |",
    "| Use Guidelines only | “Use official guidelines only.” | `$design-arc evidence guidelines` | `/design-arc:design-arc evidence guidelines` |",
    "| Report approval behavior | “What approval mode is active?” | `$design-arc mode` | `/design-arc:design-arc mode` |",
    "| Save Guided | “Pause for both approvals in this project.” | `$design-arc mode guided` | `/design-arc:design-arc mode guided` |",
    "| Save Follow recommendation | “Follow the recommendation, then show me the visual proposal.” | `$design-arc mode follow-recommendation` | `/design-arc:design-arc mode follow-recommendation` |",
    "| Save Fully automatic | “Bypass both gates for this explicit objective.” | `$design-arc mode fully-automatic` | `/design-arc:design-arc mode fully-automatic` |",
    "| Report graph state | “Is graph assistance active for this review?” | `$design-arc graph` | `/design-arc:design-arc graph` |",
    "| Save this project on | “Turn graph assistance on for this project.” | `$design-arc graph on` | `/design-arc:design-arc graph on` |",
    "| Save this project off | “Turn graph assistance off for this project.” | `$design-arc graph off` | `/design-arc:design-arc graph off` |",
    "| Explain state | “Explain why graph assistance has this state.” | `$design-arc graph explain` | `/design-arc:design-arc graph explain` |",
    "| Rebuild this review | “Rebuild this review’s graph from the current workflow evidence.” | `$design-arc graph rebuild` | `/design-arc:design-arc graph rebuild` |",
    "| Clear this review | “Clear this review’s graph; ask me to confirm first.” | `$design-arc graph clear` | `/design-arc:design-arc graph clear` |",
    "| Set laptop safety off | “Turn graph assistance off on this laptop.” | `$design-arc graph global off` | `/design-arc:design-arc graph global off` |",
    "| Remove laptop safety ceiling | “Remove the laptop-wide graph safety ceiling.” | `$design-arc graph global on` | `/design-arc:design-arc graph global on` |",
    "| Return through a project home | `$design-arc home` | Not available; Claude Code does not create a project home. |",
    "| Add a project reminder | Not available; Codex does not use a `CLAUDE.md` reminder. | Optional approved `CLAUDE.md` reminder; no command. |",
)
errors = [f"FAIL: advanced controls is missing exact action-matrix row: {row}" for row in required_matrix_rows if row not in controls]

if "The examples below use the Codex command surface" in prompts:
    errors.append("FAIL: prompt examples must not be Codex-first")
plain_section = prompts.split("## Plain-language journey starters", 1)[1].split("## ", 1)[0]
for starter in (
    "> Help me make our onboarding less confusing.",
    "> Audit how customers complete checkout and propose a better complete journey.",
    "> Redesign account recovery so people can get back in without weakening security.",
):
    if starter not in plain_section:
        errors.append("FAIL: prompt examples must put command-free journey starters first")
if "$design-arc" in plain_section or "/design-arc:design-arc" in plain_section:
    errors.append("FAIL: plain-language journey starters must be command-free")
if "Stitch gates" in prompts or "Stitch Gate" in prompts:
    errors.append("FAIL: prompt examples must not present Stitch as a required gate")
if "past Stitch" in prompts:
    errors.append("FAIL: prompt examples must not imply that approval continues past Stitch")
if "Stitch remains optional" not in prompts:
    errors.append("FAIL: prompt examples must explicitly preserve optional Stitch")
if errors:
    raise SystemExit("\n".join(errors))
PY

for beginner_page in "$readme" "$getting_started" "$using_design_arc"
do
  forbid_text "$beginner_page" '$design-arc setup'
  forbid_text "$beginner_page" '$design-arc mode'
  forbid_text "$beginner_page" '$design-arc evidence'
  forbid_text "$beginner_page" '$design-arc graph'
  forbid_text "$beginner_page" '/design-arc:design-arc graph'
done

for forbidden_shared_runtime in \
  'Generate one complete static journey board<br/>Codex by default' \
  'Codex generates the static journey board by default.' \
  'after one Codex correction round' \
  'You can stay in Codex.' \
  'The same validation and correction rules apply whether Codex or Stitch renders the screens.' \
  '## Choosing Codex or Stitch for the screens'
do
  forbid_text "$using_design_arc" "$forbidden_shared_runtime"
done

require_text "$evidence_methodology" '# Evidence and methodology'
require_text "$evidence_methodology" 'How are Design Arc recommendations grounded and validated?'
require_text "$evidence_methodology" '| Grounding layer | Pain point | How Design Arc solves it | Credible sources used |'
require_text "$evidence_methodology" '| Platform requirements | Designs can feel unfamiliar, exclude users, or conflict with platform conventions. | Validate the journey against current guidance for its actual platform. | Apple HIG; Android and Material guidance; W3C web accessibility standards. |'
require_text "$evidence_methodology" '| Product precedent | Teams copy attractive screenshots without understanding the complete journey or failure states. | Inspect relevant end-to-end product journeys and explain why a pattern fits the objective. | Authorized benchmark research through a provider such as Mobbin. |'
require_text "$evidence_methodology" '| Product judgment | Opinions and trade-offs can be presented as if a source proved them. | Tie recommendations to the confirmed objective and label judgment separately from observed evidence. | User-confirmed objective and documented Design Arc synthesis—not an external authority. |'
require_text "$evidence_methodology" '| Visualization and validation | Polished screens can conceal missing transitions, errors, and recovery states. | Visualize the complete journey and inspect every important state before approving it for frontend implementation. | AI coding platform static journey boards by default; optional Google Stitch workspace—not an evidence authority. |'
require_text "$evidence_methodology" 'A single genuine trigger is enough for Design Arc to recommend Stitch'
require_text "$evidence_methodology" 'Staying in the AI coding platform remains available, and the user always approves any transfer.'
require_text "$evidence_methodology" '| Relationship context | A correction can miss dependent states when requirements, evidence, and screens are considered separately. | Keep validated relationships visible to plan the smallest compatible correction batch and the regression checks that follow. | The current Design Arc workflow record; the relationship record adds context only. |'
require_text "$evidence_methodology" 'First-party guidance remains authoritative for its platform, authorized benchmark evidence remains precedent, the AI coding platform or Stitch provides visualization, and the graph remains relationship context only.'
require_text "$evidence_methodology" 'A graph relationship is not evidence, proof, approval, a source of requirements, or authority.'
require_text "$evidence_methodology" 'The graph can focus correction planning but never replaces complete render inspection or the proposal-wide correction limit.'
require_text "$evidence_methodology" '| Motion specification | AI coding platform + affected-platform guidance + inspected motion evidence | Defines what moves, why, how it behaves, its reduced-motion alternative, and what still requires implementation proof. |'
require_text "$evidence_methodology" 'The initial proposal may be followed by at most three correction rounds for the whole proposal.'
require_text "$evidence_methodology" 'Each round batches every known repairable mismatch, generates a new proposal, and reinspects the complete result.'
require_text "$evidence_methodology" 'A written correction is not a corrected proposal; only the inspected replacement render proves the change.'
require_text "$evidence_methodology" '### Motion grounding and implementation proof'
require_text "$evidence_methodology" 'Design Arc specifies material on-screen animations and screen-to-screen transitions before frontend implementation.'
require_text "$evidence_methodology" 'Every material motion, including retained native or existing behavior, gets a contract with: Motion ID; journey location; purpose; trigger; start/end state; spatial behavior; choreography; timing; easing/spring; interruption; reduced motion; evidence; provenance; implementation target; implementation source; proof status.'
require_text "$evidence_methodology" 'Unsupported values are `unverified`.'
require_text "$evidence_methodology" 'Static screens or sequences support only start/end state, changing element, journey location, and transition intent; they cannot support exact duration, easing, springs, velocity, interruption, or choreography.'
require_text "$evidence_methodology" 'Directly applicable native or current first-party specifications and inspected playable evidence can support temporal behavior; otherwise temporal values remain labeled Design Arc judgment or `unverified`.'
require_text "$evidence_methodology" 'Stitch prototypes are design evidence, not staging or device implementation proof.'
require_text "$evidence_methodology" 'Each direction explains motion purpose and restraint, relevant precedent and platform guidance, provenance labels, reduced-motion implications, motion-specific risks, implementation complexity, and remaining proof.'
require_text "$evidence_methodology" 'A visual verdict evaluates the same motion requirements and contract alignment, and `meets direction` records prototype limitations and remaining runtime proof before Fully automatic may continue.'
require_text "$evidence_methodology" '[Motion grounding](trusted-sources/motion.md)'
require_text "$evidence_methodology" '[Trusted sources](trusted-sources/README.md)'
require_text "$evidence_methodology" 'Next: [Upgrades and migration](upgrades-and-migration.md).'

require_text "$upgrades_migration" '# Upgrades and migration'
require_text "$upgrades_migration" 'How do I safely upgrade the installed Design Arc adapters today?'
require_text "$upgrades_migration" '## Current adapter upgrades'
require_text "$upgrades_migration" 'Codex, Claude Code, and Google Antigravity are independently installed adapters. Upgrading one never installs, removes, upgrades, or synchronizes either other adapter.'
require_text "$upgrades_migration" 'claude plugin update design-arc@design-arc-marketplace'
require_text "$upgrades_migration" 'Use a supported Google Antigravity extension update route.'
require_text "$upgrades_migration" 'Before any adapter change, verify the installed version, requested version, source, and route.'
forbid_text "$upgrades_migration" 'Before either change, verify the installed version, requested version, source, and route.'
require_text "$upgrades_migration" 'An Antigravity adapter change preserves `.gemini/design-arc.yaml`, active-review records, review artifacts, graphs, product files, and active sessions byte-for-byte.'
require_text "$upgrades_migration" 'A Claude Code adapter change preserves `.claude/design-arc.yaml`, the approved `CLAUDE.md` reminder block, reviews, graphs, product files, and active sessions byte-for-byte.'
require_text "$upgrades_migration" 'Start a new clean session in the adapter you changed; an already-open session keeps its pinned runtime and workflow version.'
require_text "$upgrades_migration" 'For retired plugin replacement, legacy Codex preference import, and 0.2–0.3 recovery, read [Migration history](migration-history.md).'
require_text "$upgrades_migration" 'For the current one-time Codex-to-Claude portable preference import, read [Design Arc for Claude Code](claude-code.md#import-portable-preferences-from-codex).'
forbidden_current_history='codex plugin remove fb-ux@fb-ux-marketplace
codex plugin remove apple-guidelines-stitch@fb-ux-marketplace
### Moving to or from 0.3.0
### Upgrading from 0.3.0 to 0.3.1
Saved preferences and migration'
while IFS= read -r historical_text
do
  forbid_text "$upgrades_migration" "$historical_text"
done <<EOF
$forbidden_current_history
EOF
require_text "$upgrades_migration" 'Next: [Trust and sources](trust-limitations-and-sources.md).'

require_text "$migration_history" '# Migration history (legacy compatibility)'
require_text "$migration_history" 'This page preserves retired replacement and recovery instructions. It is not the current upgrade path.'
require_text "$migration_history" 'For current adapter upgrades and preservation rules, read [Upgrades and migration](upgrades-and-migration.md).'
require_text "$migration_history" 'codex plugin remove fb-ux@fb-ux-marketplace'
require_text "$migration_history" 'codex plugin remove apple-guidelines-stitch@fb-ux-marketplace'
require_text "$migration_history" 'codex plugin marketplace remove fb-ux-marketplace'
require_text "$migration_history" 'codex plugin marketplace add friedbeef1/design-arc --ref main'
require_text "$migration_history" 'codex plugin add design-arc@design-arc-marketplace'
require_text "$migration_history" 'Start a new Codex task.'
require_text "$migration_history" 'Never silently merge, rewrite, or delete either legacy preference file.'
require_text "$migration_history" '### Moving to or from 0.3.0'
require_text "$migration_history" 'Upgrading to 0.3.0 preserves project preferences, homes, active-review identity and workflow versions, graph records, and product files.'
require_text "$migration_history" 'Active reviews are not changed mid-review; a later clean review resolves the 0.3.0 default independently.'
require_text "$migration_history" 'Downgrading to an older workflow leaves graph records in place but ignores them; it does not delete or reinterpret them.'
require_text "$migration_history" '### Upgrading from 0.3.0 to 0.3.1'
require_text "$migration_history" 'Version `0.3.1` adds an activation-integrity boundary.'
require_text "$migration_history" 'Automatic selection is not guaranteed, so an unprefixed response is never presented as Design Arc work unless the skill actually loaded.'
require_text "$migration_history" 'The patch does not rewrite project preferences, recreate pinned homes, change product files, alter graph records, or convert active reviews.'

require_text "$trust_sources" '# Trust, limitations and sources'
require_text "$trust_sources" 'What can Design Arc prove, access, implement, or release?'
require_text "$trust_sources" 'The AI coding platform—Codex, Claude Code, or Google Antigravity—generates static journey boards by default.'
require_text "$trust_sources" 'Installing any one of the three adapters authorizes only that local adapter installation.'
require_text "$trust_sources" 'Benchmark, browser, visualization, MCP, provider, and product access each require their own authorization, including approval for the data sent.'
require_text "$trust_sources" '## Claude Code, Claude Desktop, and MCP'
require_text "$trust_sources" 'Design Arc 1.5.2 is packaged and verified for Claude Code.'
forbid_text "$trust_sources" 'Codex or Claude Code generates static journey boards in the AI coding platform by default.'
forbid_text "$trust_sources" 'Installing either adapter authorizes only that local plugin installation.'
forbid_text "$trust_sources" 'Design Arc 0.4.0 is packaged and verified for Claude Code.'
require_text "$trust_sources" 'It is not a Claude Desktop chat extension and does not install or configure a Desktop MCP server.'
require_text "$trust_sources" 'Claude Desktop chat MCP configuration is separate from Claude Code configuration.'
require_text "$trust_sources" '[Anthropic’s Claude Code Desktop guide](https://code.claude.com/docs/en/desktop)'
require_text "$trust_sources" '[Anthropic’s MCP guide](https://code.claude.com/docs/en/mcp)'
require_text "$trust_sources" 'access is not bundled by Design Arc'
require_text "$trust_sources" 'The Live Codex edition is published in the OpenAI Plugin Directory.'
require_text "$trust_sources" 'Deterministic tests protect the written workflow contract, but they do not prove every future runtime response.'
require_text "$trust_sources" 'Graph assistance is a project-local relationship record for correction planning, not a new source of truth.'
require_text "$trust_sources" 'It cannot prove a requirement, establish runtime quality, replace current evidence, or authorize a product decision.'
require_text "$trust_sources" 'A failed graph record reduces assistance rather than blocking the review: Design Arc reports the issue and continues the standard workflow.'
require_text "$trust_sources" '[Trusted sources](trusted-sources/README.md)'
require_text "$trust_sources" '[Runtime boundaries](runtime-boundaries.md)'
require_text "$trust_sources" 'Next: [Home](../README.md).'

require_text "$trusted_source_library" '| Visualization and validation | A concrete proposed journey that can be inspected across material states. | AI coding platform static journey boards by default; optional [Google Stitch](https://stitch.withgoogle.com/) workspace. | Evidence, platform compliance, accessibility, or implementation readiness by itself. |'
require_text "$trusted_source_library" '[Visualization](visualization.md) — platform static boards by default and Stitch as an optional persistent editing workspace.'
require_text "$visualization_sources" 'Design Arc generates a consolidated static journey board in the AI coding platform by default: Codex for the Codex adapter, Claude Code for the Claude adapter, and Google Antigravity for the Antigravity adapter.'
require_text "$visualization_sources" 'The AI coding platform is the lower-friction route for a bounded proposal and a few corrections.'
require_text "$runtime_boundaries" '# Runtime boundaries'
require_text "$runtime_boundaries" 'Design Arc is one shared workflow. The AI coding platform owns only the runtime-specific installation, invocation, saved state, return path, visualization capability, and upgrade behavior.'
require_text "$runtime_boundaries" 'The [Codex runtime](codex.md), [Claude Code runtime](claude-code.md), and [Google Antigravity runtime](antigravity.md) pages are the authoritative guides for those platform-specific details.'
require_text "$runtime_boundaries" 'Codex, Claude Code, and Google Antigravity never merge, migrate, resume, or continue an active review across runtimes.'
require_text "$runtime_boundaries" 'Objective Confirmation, both evidence modes, the Direction Gate, the Visual Proposal Gate, complete-state validation, optional Stitch, and the three-round correction limit are shared workflow contracts.'
require_text "$runtime_boundaries" 'No runtime detail or approval authorizes source implementation, staging, deployment, or release.'
require_text "$operating_layer" '# Codex operating layer (compatibility page)'
require_text "$operating_layer" 'The authoritative shared boundary is [Runtime boundaries](runtime-boundaries.md).'
require_text "$operating_layer" '[Design Arc for Codex](codex.md)'

for shared_page in "$readme" "$getting_started" "$using_design_arc" "$evidence_methodology" "$trust_sources" "$faq"
do
  for forbidden_codex_default in \
    'Codex generates the static journey board by default.' \
    'Codex creates static screen images and complete journey boards directly by default.' \
    'You can stay in Codex.' \
    'Codex as the Design Arc operating layer' \
    'ask for Design Arc by name or use a confirmed Codex project home when you want certainty.'
  do
    forbid_text "$shared_page" "$forbidden_codex_default"
  done
done

for shared_doc in "$evidence_methodology" "$trusted_source_library" "$visualization_sources"
do
  for forbidden_shared_runtime in \
    'Codex-generated static journey boards by default' \
    'Codex generates one consolidated static journey board by default' \
    'Staying in Codex remains available' \
    'Codex static boards by default'
  do
    forbid_text "$shared_doc" "$forbidden_shared_runtime"
  done
done

python3 - "$readme" "$advanced_controls" "$evidence_methodology" "$upgrades_migration" "$migration_history" "$trust_sources" <<'PY'
from pathlib import Path
import re
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
advanced_controls = Path(sys.argv[2]).read_text(encoding="utf-8")
methodology = Path(sys.argv[3]).read_text(encoding="utf-8")
migration = Path(sys.argv[4]).read_text(encoding="utf-8")
migration_history = Path(sys.argv[5]).read_text(encoding="utf-8")
trust = Path(sys.argv[6]).read_text(encoding="utf-8")
marketplace_command = "codex plugin marketplace add friedbeef1/design-arc --ref main"
plugin_command = "codex plugin add design-arc@design-arc-marketplace"
if marketplace_command not in advanced_controls:
    raise SystemExit("FAIL: advanced controls must include the exact marketplace command")
if plugin_command not in advanced_controls:
    raise SystemExit("FAIL: advanced controls must include the exact Design Arc install command")
marketplace_position = advanced_controls.index(marketplace_command)
plugin_position = advanced_controls.index(plugin_command)
if marketplace_position > plugin_position:
    raise SystemExit("FAIL: advanced controls must add the marketplace before adding Design Arc")
if "Codex handles the installation" in advanced_controls:
    raise SystemExit("FAIL: README must not promise that Codex infers the marketplace route automatically")
if "skills.sh URL or package name" in advanced_controls:
    raise SystemExit("FAIL: troubleshooting must not route Design Arc back to a standalone skills registry")
if "Visual Gate" in "".join((text, advanced_controls, methodology, migration, trust)):
    raise SystemExit("FAIL: documentation must use the required Visual Proposal Gate name, not Visual Gate")

local_command = "codex plugin marketplace add /path/to/design-arc"
if local_command not in advanced_controls.splitlines():
    raise SystemExit("FAIL: advanced controls must show the exact local-checkout marketplace command")
if f"{local_command} --ref main" in advanced_controls:
    raise SystemExit("FAIL: documentation local-checkout marketplace command must not use the Git-only --ref option")

headings = re.findall(r"^#{1,2} .+$", text, re.MULTILINE)
expected_headings = [
    "# Design Arc",
    "## Documentation",
    "## One product, three platform editions",
    "## You need Design Arc if…",
    "## What Design Arc produces",
    "## The workflow",
    "## Install",
    "## Start a review",
    "## Trust",
    "## License",
]
if headings != expected_headings:
    raise SystemExit("FAIL: README sections are not in the approved landing-page order")

workflow_start = text.index("## The workflow")
workflow_end = text.index("## Install")
workflow = text[workflow_start:workflow_end]
workflow_instruction = "**Rows marked 👤 You show where your involvement may be needed. First-use choices, approval pauses, and the optional Stitch choice are conditional.**"
workflow_table = """| Workflow step | Platform or source handling it | Human involvement |
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
| Prepare the design handoff | AI coding platform | |"""

def validate_workflow(candidate):
    expected_table = f"## The workflow\n\n{workflow_instruction}\n\n{workflow_table}"
    following_prose = "Setup resolves two independent choices: how evidence is gathered and where Design Arc pauses for approval."
    if not candidate.startswith(expected_table):
        raise ValueError("workflow must use the exact instruction, table header, separator, and ordered rows")
    if not candidate[len(expected_table):].startswith(f"\n\n{following_prose}"):
        raise ValueError("workflow table must end immediately after the final handoff row")
    if candidate.count("| ↓ | | |") != 12:
        raise ValueError("workflow must preserve the 12-row arrow sequence")
    if candidate.count("👤 You") != 6:
        raise ValueError("workflow must contain one legend reference and five human-involvement rows")

validate_workflow(workflow)

for mutated_workflow in (
    workflow.replace(workflow_instruction, "**Design Arc handles every step.**", 1),
    workflow.replace("| Workflow step | Platform or source handling it | Human involvement |", "| Workflow | Platform | Human |", 1),
    workflow.replace(
        "| Describe the outcome you want | AI coding platform | **👤 You** |\n| ↓ | | |\n| Choose evidence and approval behavior on first use | AI coding platform | **👤 You — only when no saved preference exists** |",
        "| Choose evidence and approval behavior on first use | AI coding platform | **👤 You — only when no saved preference exists** |\n| ↓ | | |\n| Describe the outcome you want | AI coding platform | **👤 You** |",
        1,
    ),
    workflow.replace(
        "| Prepare the design handoff | AI coding platform | |\n\nSetup resolves",
        "| Prepare the design handoff | AI coding platform | |\n| Record a follow-up | AI coding platform | |\n\nSetup resolves",
        1,
    ),
):
    try:
        validate_workflow(mutated_workflow)
    except ValueError:
        pass
    else:
        raise SystemExit("FAIL: workflow contract must reject instruction, header, row-order, and extra-row mutations")
print("PASS: workflow contract rejects instruction, header, row-order, and extra-row mutations")

for superseded_label in (
    "**Only the bold steps need you. Design Arc handles everything else.**",
    "**Choose preferences once**",
    "**Authorize external access if requested**",
    "**Approve the direction if your mode pauses**",
    "**Approve the visual proposal if your mode pauses**",
    "→",
):
    if superseded_label in workflow:
        raise SystemExit(f"FAIL: workflow retains superseded horizontal/manual label: {superseded_label}")

for provider in ("Apple", "Mobbin", "Stitch"):
    if provider not in methodology:
        raise SystemExit(f"FAIL: {provider} is missing from evidence and methodology")

migration_commands = [
    "codex plugin remove fb-ux@fb-ux-marketplace",
    "codex plugin remove apple-guidelines-stitch@fb-ux-marketplace",
    "codex plugin marketplace remove fb-ux-marketplace",
    "codex plugin marketplace add friedbeef1/design-arc --ref main",
    "codex plugin add design-arc@design-arc-marketplace",
    "Start a new Codex task.",
]
migration_positions = [migration_history.index(command) for command in migration_commands]
if migration_positions != sorted(migration_positions):
    raise SystemExit("FAIL: migration steps are not in the required safe order")

trusted_sources_dir = Path(sys.argv[1]).parent / "docs" / "trusted-sources"
approved_external_urls = {
    "https://developer.apple.com/design/human-interface-guidelines/",
    "https://developer.android.com/design/ui/mobile",
    "https://developer.android.com/guide/topics/ui/accessibility",
    "https://m3.material.io/",
    "https://www.w3.org/TR/WCAG22/",
    "https://www.w3.org/WAI/ARIA/apg/",
    "https://mobbin.com/",
    "https://stitch.withgoogle.com/",
    "https://developer.apple.com/design/human-interface-guidelines/motion",
    "https://developer.android.com/develop/ui/compose/animation/introduction",
    "https://m3.material.io/styles/motion/overview/how-it-works",
    "https://www.w3.org/TR/mediaqueries-5/#prefers-reduced-motion",
    "https://docs.mobbin.com/mcp/introduction",
    "https://motion.dev/docs/quick-start",
    "https://motion.dev/docs/ai-kit-install",
    "https://pageflows.com/",
}
actual_external_urls = {
    url
    for path in trusted_sources_dir.glob("*.md")
    for url in re.findall(r"https?://[^\s)]+", path.read_text(encoding="utf-8"))
}
if actual_external_urls != approved_external_urls:
    missing = sorted(approved_external_urls - actual_external_urls)
    unexpected = sorted(actual_external_urls - approved_external_urls)
    raise SystemExit(
        "FAIL: trusted sources external URL set drifted"
        f"; missing={missing}; unexpected={unexpected}"
    )
PY


require_text "$repo_root/docs/trusted-sources/platform-guidance.md" '## Motion guidance'
require_text "$repo_root/docs/trusted-sources/platform-guidance.md" 'Existing product motion and standard native behavior come first.'
require_text "$repo_root/docs/trusted-sources/platform-guidance.md" 'A screenshot or static screen sequence cannot prove exact motion timing, easing, velocity, spring behavior, or choreography.'

require_text "$repo_root/docs/trusted-sources/README.md" '[Motion grounding](motion.md)'
require_text "$motion_sources" '# Motion grounding'
require_text "$motion_sources" 'Motion needs evidence because it changes what people perceive, control, and can tolerate, not just how a screen looks.'
require_text "$motion_sources" 'Shipped-product precedent shows what was observed in a comparable journey; an implementation library supplies tools, not proof that its defaults fit this product.'
require_text "$motion_sources" 'A static Mobbin screen or sequence can establish only the visible states, changing element, journey location, and intended transition.'
require_text "$motion_sources" 'Use a recording or playable journey when the decision depends on timing, easing, spring behavior, velocity, choreography, interruption, reversal, or a missing intermediate state.'
require_text "$motion_sources" 'Motion and Motion+ are optional implementation dependencies, never Design Arc requirements, evidence, authority, or bundled dependencies.'
require_text "$motion_sources" 'After separate authorization, Motion+ can assist an implementation owner with documentation and example search, reusable source retrieval, spring and easing work, saved-transition inspection, performance auditing, and design-system adaptation.'
require_text "$motion_sources" 'Implementation targets name the runtime and UI technology, such as Web, React, SwiftUI, UIKit, or Compose; timing uses milliseconds or seconds or a parameterized physical spring; easing uses cubic-bezier values, a named platform curve, or reproducible spring parameters.'
require_text "$motion_sources" 'Interruption covers reversal, cancellation, and re-entry; provenance carries one required label plus citations and estimate basis; implementation source records authorization; proof status distinguishes specified, prototyped, staging, device, and production evidence.'
require_text "$motion_sources" 'For Android and web targets, their current first-party guidance takes precedence over conflicting Apple-inspired judgment.'
require_text "$motion_sources" 'Every material motion contract must name a reduced-motion alternative; no animation is the fallback only when it still preserves the needed information and control.'
require_text "$motion_sources" 'A prototype can communicate an intended interaction, but it cannot prove runtime quality.'

require_text "$prompts" '# Design Arc prompt examples'
require_text "$prompts" 'Start in ordinary language in either runtime.'
require_text "$prompts" 'automatic skill selection is not guaranteed'
require_text "$prompts" '## Plain-language journey starters'
require_text "$prompts" '> Help me make our onboarding less confusing.'
require_text "$prompts" '> Audit how customers complete checkout and propose a better complete journey.'
require_text "$prompts" '> Redesign account recovery so people can get back in without weakening security.'
require_text "$prompts" '## Optional command forms'
require_text "$prompts" '$design-arc setup'
require_text "$prompts" '/design-arc:design-arc setup'
require_text "$prompts" '$design-arc evidence benchmarks'
require_text "$prompts" '/design-arc:design-arc evidence benchmarks'
require_text "$prompts" '$design-arc evidence guidelines'
require_text "$prompts" '/design-arc:design-arc evidence guidelines'
require_text "$prompts" '$design-arc mode guided'
require_text "$prompts" '/design-arc:design-arc mode guided'
require_text "$prompts" '$design-arc mode follow-recommendation'
require_text "$prompts" '/design-arc:design-arc mode follow-recommendation'
require_text "$prompts" '$design-arc mode fully-automatic'
require_text "$prompts" '/design-arc:design-arc mode fully-automatic'
require_text "$prompts" 'use Guidelines only for this run'
require_text "$prompts" 'Bypass both gates'
forbid_text "$prompts" 'stop at the Stitch Gate'
forbid_text "$prompts" 'continues through Stitch only when the verdict'

printf '%s\n' 'PASS: Design Arc product documentation'

if [ "${DESIGN_ARC_DOCS_SKIP_BROKEN_LINK_MUTATION:-}" != '1' ]
then
  mutation_checkout="$task_temp_dir/broken-link-fixture"
  copy_fixture "$mutation_checkout"
  mutation_page="$mutation_checkout/README.md"

  python3 - "$mutation_page" <<'PY'
from pathlib import Path
import sys

page = Path(sys.argv[1])
original = page.read_text(encoding="utf-8")
target = "[Learn how to use Design Arc.](docs/using-design-arc.md)"
if target not in original:
    raise SystemExit("FAIL: broken-link fixture requires a valid menu target")
page.write_text(original.replace(target, "[Learn how to use Design Arc.](missing-page.md)", 1), encoding="utf-8")
PY

  if output=$(DESIGN_ARC_DOCS_SKIP_BROKEN_LINK_MUTATION=1 sh "$mutation_checkout/scripts/test-design-arc-docs.sh" 2>&1)
  then
    printf '%s\n' "$output" >&2
    fail 'broken-link mutation was accepted'
  fi

  printf '%s\n' "$output" | grep -F 'FAIL: broken relative link in' >/dev/null || {
    printf '%s\n' "$output" >&2
    fail 'broken-link mutation failed for the wrong reason'
  }
  printf '%s\n' 'PASS: broken-link mutation is rejected'

  escape_checkout="$task_temp_dir/escape-link-fixture"
  copy_fixture "$escape_checkout"
  escape_page="$escape_checkout/README.md"

  python3 - "$escape_page" <<'PY'
from pathlib import Path
import os
import sys

page = Path(sys.argv[1])
original = page.read_text(encoding="utf-8")
target = "[Learn how to use Design Arc.](docs/using-design-arc.md)"
if target not in original:
    raise SystemExit("FAIL: escape-link fixture requires a valid menu target")
escape_target = os.path.relpath("/etc/passwd", page.parent)
page.write_text(
    original.replace(target, f"[Learn how to use Design Arc.]({escape_target})", 1),
    encoding="utf-8",
)
PY

  if output=$(DESIGN_ARC_DOCS_SKIP_BROKEN_LINK_MUTATION=1 sh "$escape_checkout/scripts/test-design-arc-docs.sh" 2>&1)
  then
    printf '%s\n' "$output" >&2
    fail 'escape-link mutation was accepted'
  fi

  printf '%s\n' "$output" | grep -F 'FAIL: relative link escapes repository in' >/dev/null || {
    printf '%s\n' "$output" >&2
    fail 'escape-link mutation failed for the wrong reason'
  }
  printf '%s\n' 'PASS: escape-link mutation is rejected'

  fragment_checkout="$task_temp_dir/broken-fragment-fixture"
  copy_fixture "$fragment_checkout"
  fragment_page="$fragment_checkout/docs/codex.md"

  python3 - "$fragment_page" <<'PY'
from pathlib import Path
import sys

page = Path(sys.argv[1])
original = page.read_text(encoding="utf-8")
target = "[Projects and AI coding platforms](faq.md#projects-and-ai-coding-platforms)"
if target not in original:
    raise SystemExit("FAIL: broken-fragment fixture requires the exact Codex FAQ link")
page.write_text(original.replace(target, "[Projects and AI coding platforms](faq.md#missing-project-home)", 1), encoding="utf-8")
PY

  if output=$(DESIGN_ARC_DOCS_SKIP_BROKEN_LINK_MUTATION=1 sh "$fragment_checkout/scripts/test-design-arc-docs.sh" 2>&1)
  then
    printf '%s\n' "$output" >&2
    fail 'broken-fragment mutation was accepted'
  fi

  printf '%s\n' "$output" | grep -F 'FAIL: broken Markdown fragment in' >/dev/null || {
    printf '%s\n' "$output" >&2
    fail 'broken-fragment mutation failed for the wrong reason'
  }
  printf '%s\n' 'PASS: broken-fragment mutation is rejected'

  license_checkout="$task_temp_dir/license-link-fixture"
  copy_fixture "$license_checkout"
  license_page="$license_checkout/README.md"

  python3 - "$license_page" <<'PY'
from pathlib import Path
import sys

page = Path(sys.argv[1])
original = page.read_text(encoding="utf-8")
target = "[MIT License](LICENSE)"
if target not in original:
    raise SystemExit("FAIL: license-link fixture requires the exact README licence link")
page.write_text(original.replace(target, "[MIT licence](LICENSE)", 1), encoding="utf-8")
PY

  if output=$(DESIGN_ARC_DOCS_SKIP_BROKEN_LINK_MUTATION=1 sh "$license_checkout/scripts/test-design-arc-docs.sh" 2>&1)
  then
    printf '%s\n' "$output" >&2
    fail 'license-link mutation was accepted'
  fi

  printf '%s\n' "$output" | grep -F 'missing required text in README.md: [MIT License](LICENSE)' >/dev/null || {
    printf '%s\n' "$output" >&2
    fail 'license-link mutation failed for the wrong reason'
  }
  printf '%s\n' 'PASS: license-link mutation is rejected'

  missing_action_resource_checkout="$task_temp_dir/missing-action-resource-fixture"
  copy_fixture "$missing_action_resource_checkout"
  missing_action_resource_page="$missing_action_resource_checkout/README.md"

  python3 - "$missing_action_resource_page" <<'PY'
from pathlib import Path
import sys

page = Path(sys.argv[1])
original = page.read_text(encoding="utf-8")
target = "[Open presentation](https://docs.google.com/presentation/d/1EG5vrPC5UqAkNAr9jce0lvZz1Jq5oI4AqAbPVivG2sU/preview)"
if target not in original:
    raise SystemExit("FAIL: missing-action-resource fixture requires the introduction-deck fallback")
page.write_text(original.replace(target, "Open presentation", 1), encoding="utf-8")
PY

  if output=$(DESIGN_ARC_DOCS_SKIP_BROKEN_LINK_MUTATION=1 sh "$missing_action_resource_checkout/scripts/test-design-arc-docs.sh" 2>&1)
  then
    printf '%s\n' "$output" >&2
    fail 'missing action resource mutation was accepted'
  fi

  printf '%s\n' "$output" | grep -F 'FAIL: README action section must retain the ordered two-card demo and introduction-deck resources' >/dev/null || {
    printf '%s\n' "$output" >&2
    fail 'missing action resource mutation failed for the wrong reason'
  }
  printf '%s\n' 'PASS: missing action resource mutation is rejected'

  reordered_action_resource_checkout="$task_temp_dir/reordered-action-resource-fixture"
  copy_fixture "$reordered_action_resource_checkout"
  reordered_action_resource_page="$reordered_action_resource_checkout/README.md"

  python3 - "$reordered_action_resource_page" <<'PY'
from pathlib import Path
import sys

page = Path(sys.argv[1])
original = page.read_text(encoding="utf-8")
target = "| Product walkthrough | Introduction deck |"
if target not in original:
    raise SystemExit("FAIL: reordered-action-resource fixture requires the action-card headers")
page.write_text(original.replace(target, "| Introduction deck | Product walkthrough |", 1), encoding="utf-8")
PY

  if output=$(DESIGN_ARC_DOCS_SKIP_BROKEN_LINK_MUTATION=1 sh "$reordered_action_resource_checkout/scripts/test-design-arc-docs.sh" 2>&1)
  then
    printf '%s\n' "$output" >&2
    fail 'reordered action resource mutation was accepted'
  fi

  printf '%s\n' "$output" | grep -F 'FAIL: README action section must retain the ordered two-card demo and introduction-deck resources' >/dev/null || {
    printf '%s\n' "$output" >&2
    fail 'reordered action resource mutation failed for the wrong reason'
  }
  printf '%s\n' 'PASS: reordered action resource mutation is rejected'

  command_order_checkout="$task_temp_dir/plugin-command-order-fixture"
  copy_fixture "$command_order_checkout"
  command_order_page="$command_order_checkout/docs/advanced-controls.md"

  python3 - "$command_order_page" <<'PY'
from pathlib import Path
import sys

page = Path(sys.argv[1])
original = page.read_text(encoding="utf-8")
marketplace_command = "codex plugin marketplace add friedbeef1/design-arc --ref main"
plugin_command = "codex plugin add design-arc@design-arc-marketplace"
ordered_commands = f"{marketplace_command}\n{plugin_command}"
if ordered_commands not in original:
    raise SystemExit("FAIL: plugin-command-order fixture requires the ordered installation commands")
page.write_text(original.replace(ordered_commands, f"{plugin_command}\n{marketplace_command}", 1), encoding="utf-8")
PY

  if output=$(DESIGN_ARC_DOCS_SKIP_BROKEN_LINK_MUTATION=1 sh "$command_order_checkout/scripts/test-design-arc-docs.sh" 2>&1)
  then
    printf '%s\n' "$output" >&2
    fail 'plugin-command-order mutation was accepted'
  fi

  printf '%s\n' "$output" | grep -F 'FAIL: advanced controls must add the marketplace before adding Design Arc' >/dev/null || {
    printf '%s\n' "$output" >&2
    fail 'plugin-command-order mutation failed for the wrong reason'
  }
  printf '%s\n' 'PASS: plugin-command-order mutation is rejected'
fi
