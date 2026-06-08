import re
import sys
import subprocess
import argparse

def get_pr_number():
    """Fetches the current PR number if available."""
    result = subprocess.run(["gh", "pr", "view", "--json", "number", "--jq", ".number"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error fetching PR number (exit code: {result.returncode}):", file=sys.stderr)
        print("Command: gh pr view --json number --jq .number", file=sys.stderr)
        print(f"Error: {result.stderr}", file=sys.stderr)
        print("Please ensure:", file=sys.stderr)
        print("1. You are on a PR branch", file=sys.stderr)
        print("2. GitHub CLI (gh) is installed and authenticated", file=sys.stderr)
        print("3. You have access to the repository", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()

def get_pr_diff(pr_number):
    """Fetches the PR diff using GitHub CLI. gh infers the repo from the current directory."""
    cmd = ["gh", "pr", "diff", str(pr_number)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error fetching PR diff (exit code: {result.returncode}):", file=sys.stderr)
        print(f"Command: {' '.join(cmd)}", file=sys.stderr)
        print(f"Error: {result.stderr}", file=sys.stderr)
        print("Please ensure:", file=sys.stderr)
        print(f"1. PR #{pr_number} exists and you are in the right repository", file=sys.stderr)
        print("2. You have access to view the PR", file=sys.stderr)
        print("3. GitHub CLI (gh) is authenticated", file=sys.stderr)
        sys.exit(1)
    return result.stdout

# Matches a unified-diff hunk header, capturing the old/new start lines and
# the trailing function context: "@@ -10,7 +20,8 @@ def foo():"
HUNK_HEADER_RE = re.compile(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@(.*)')

def parse_diff(diff_text):
    result = []
    old_line_no = 0
    new_line_no = 0
    in_hunk = False

    for line in diff_text.splitlines():
        file_match = re.match(r'^diff --git a/(.+) b/(.+)', line)
        if file_match:
            result.append(f"## File: '{file_match.group(2)}'")
            in_hunk = False  # Reset when a new file starts
            continue

        hunk_match = HUNK_HEADER_RE.match(line)
        if hunk_match:
            old_line_no = int(hunk_match.group(1))
            new_line_no = int(hunk_match.group(2))
            result.append(f"\n@@ ... @@{hunk_match.group(3)}")
            in_hunk = True
            continue

        # Skip diff metadata (index, mode, ---/+++ headers) before the first hunk
        if not in_hunk:
            continue

        # "\ No newline at end of file" marker carries no line number
        if line.startswith('\\'):
            continue

        if line.startswith('+') and not line.startswith('+++'):
            # Added line: number is the new-file line (RIGHT side)
            result.append(f"{new_line_no} +{line[1:]}")
            new_line_no += 1
        elif line.startswith('-') and not line.startswith('---'):
            # Removed line: number is the old-file line (LEFT side)
            result.append(f"{old_line_no} -{line[1:]}")
            old_line_no += 1
        else:
            # Context line exists in both versions; show the new-file number
            content = line[1:] if line.startswith(' ') else line
            result.append(f"{new_line_no}  {content}")
            old_line_no += 1
            new_line_no += 1

    return "\n".join(result)

# Past this many output lines the diff likely won't fit comfortably in a model's
# context, so warn (on stderr) that the review may end up partial.
LARGE_DIFF_LINE_WARNING = 20000

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and format a GitHub PR diff for review.")
    parser.add_argument(
        "pr_number",
        nargs="?",
        help="PR number to fetch. Defaults to the PR of the current branch.",
    )
    args = parser.parse_args()

    pr_number = args.pr_number if args.pr_number else get_pr_number()

    # Reject malformed input early: a PR number is always digits.
    if not str(pr_number).isdigit():
        print(f"Error: PR number must be a positive integer (got: {pr_number})", file=sys.stderr)
        sys.exit(1)

    diff_content = get_pr_diff(pr_number)
    parsed_diff = parse_diff(diff_content)

    line_count = parsed_diff.count("\n") + 1 if parsed_diff else 0
    if line_count > LARGE_DIFF_LINE_WARNING:
        print(
            f"Warning: the parsed diff is {line_count} lines "
            f"(> {LARGE_DIFF_LINE_WARNING}); the review may be partial. "
            "Consider reviewing it in smaller chunks.",
            file=sys.stderr,
        )

    print(parsed_diff)
