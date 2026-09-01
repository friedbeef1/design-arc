#!/bin/sh
# Pressure-test Design Arc repository validation and its safety controls.

set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(CDPATH= cd "$script_dir/.." && pwd)
validator="$script_dir/validate.sh"
task_temp_dir=$(mktemp -d "${TMPDIR:-/tmp}/design-arc-validator-tests.XXXXXX")

cleanup() {
  [ -n "$task_temp_dir" ] && [ -d "$task_temp_dir" ] && rm -rf "$task_temp_dir"
}

fail() {
  printf '%s\n' "FAIL: $*" >&2
  exit 1
}

trap cleanup EXIT HUP INT TERM

expect_credential_rejection() {
  label=$1
  assignment=$2
  case_dir="$task_temp_dir/$label"
  mkdir "$case_dir"
  printf '%s\n' "$assignment" > "$case_dir/fixture.env"

  if output=$(VALIDATE_EXTRA_SCAN_ROOT="$case_dir" "$validator" 2>&1)
  then
    printf '%s\n' "$output" >&2
    fail "$label credential fixture was accepted"
  fi

  printf '%s\n' "$output" | grep -F 'FAIL: private key or credential assignment found' >/dev/null || {
    printf '%s\n' "$output" >&2
    fail "$label credential fixture failed for the wrong reason"
  }
  printf '%s\n' "PASS: rejected $label credential assignment"
}

github_token_name='GITHUB_''TOKEN'
openai_key_name='OPENAI_''API_KEY'
api_key_name='api_''key'
client_secret_name='client_''secret'

expect_credential_rejection export "export ${github_token_name}=test-placeholder"
expect_credential_rejection env "env ${openai_key_name}=test-placeholder"
expect_credential_rejection repeated-prefixes "export env ${github_token_name}=test-placeholder"
expect_credential_rejection quoted-json "{\"${api_key_name}\": \"test-placeholder\"}"
expect_credential_rejection quoted-yaml "\"${client_secret_name}\": \"test-placeholder\""

ordinary_prose_dir="$task_temp_dir/ordinary-prose"
mkdir "$ordinary_prose_dir"
printf '%s\n' 'Ask the provider how an API key is rotated before changing configuration.' > "$ordinary_prose_dir/README.md"
if ! VALIDATE_EXTRA_SCAN_ROOT="$ordinary_prose_dir" "$validator" >/dev/null
then
  fail 'ordinary credential-related prose was rejected'
fi
printf '%s\n' 'PASS: accepted ordinary credential-related prose'
printf '%s\n' 'PASS: validator negative cases'

sh "$repo_root/scripts/test-design-arc-identity.sh"
sh "$repo_root/scripts/test-design-arc-docs.sh"
python3 "$repo_root/scripts/test-workflow-contracts.py"
python3 "$repo_root/scripts/test-skill-composition.py"
python3 "$repo_root/scripts/test-graph-records.py"

if validation_output=$("$validator" 2>&1)
then
  :
else
  printf '%s\n' "$validation_output" >&2
  fail 'Design Arc repository validation failed'
fi

for expected_output in \
  'PASS: required Design Arc files' \
  'PASS: plugin and embedded skill validation for Design Arc' \
  'PASS: accepted valid fixture valid.json' \
  'PASS: isolated Design Arc plugin installation smoke' \
  'PASS: isolated Claude Code Design Arc marketplace install and load smoke' \
  'PASS: isolated Design Arc plugin migration smoke' \
  'PASS: isolated Design Arc plugin upgrade smoke' \
  'PASS: exact 0.2.3 downgrade ignores unsupported graph machinery and preserves graph records/state' \
  'PASS: isolated Design Arc 0.3.1 to 1.5.3 upgrade' \
  'PASS: credential, local-path, and media safety scans' \
  'PASS: composition check enforces version parity and package containment' \
  'PASS: shell and Python syntax checks' \
  'PASS: Design Arc repository validation'
do
  printf '%s\n' "$validation_output" | grep -F "$expected_output" >/dev/null || {
    printf '%s\n' "$validation_output" >&2
    fail "repository validation omitted expected subcheck: $expected_output"
  }
done

printf '%s\n' 'PASS: repository validation runs every Design Arc subcheck'
