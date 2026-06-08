import re
import sys
import subprocess
import argparse

def get_repo():
    """Fetches the GitHub repository (owner/repo) from the current branch's remote."""
    result = subprocess.run(["git", "config", "--get", "remote.origin.url"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error fetching repository details (exit code: {result.returncode}):")
        print("Command: git config --get remote.origin.url")
        print(f"Error: {result.stderr}")
        print("Please ensure you are in a git repository with a remote origin configured.")
        exit(1)
    repo_url = result.stdout.strip()

    # Handles both SSH (git@github.com:owner/repo.git) and HTTPS (https://github.com/owner/repo.git).
    # Only the trailing ".git" is stripped, so repo names containing dots are preserved.
    match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$', repo_url)
    if not match:
        print(f"Error: Could not parse owner/repo from remote URL: {repo_url}")
        exit(1)
    owner, repo = match.group(1), match.group(2)

    return f"{owner}/{repo}"

def get_pr_number():
    """Fetches the current PR number if available."""
    result = subprocess.run(["gh", "pr", "view", "--json", "number", "--jq", ".number"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error fetching PR number (exit code: {result.returncode}):")
        print("Command: gh pr view --json number --jq .number")
        print(f"Error: {result.stderr}")
        print("Please ensure:")
        print("1. You are on a PR branch")
        print("2. GitHub CLI (gh) is installed and authenticated")
        print("3. You have access to the repository")
        exit(1)
    return result.stdout.strip()

def get_pr_diff(pr_number, repo):
    """Fetches the PR diff using GitHub CLI."""
    cmd = ["gh", "pr", "diff", str(pr_number), "--repo", repo]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error fetching PR diff (exit code: {result.returncode}):")
        print(f"Command: {' '.join(cmd)}")
        print(f"Error: {result.stderr}")
        print("Please ensure:")
        print(f"1. PR #{pr_number} exists in repository {repo}")
        print("2. You have access to view the PR")
        print("3. GitHub CLI (gh) is authenticated")
        exit(1)
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

    repo = get_repo()
    pr_number = args.pr_number if args.pr_number else get_pr_number()

    # Guard against shell/command injection and malformed input: a PR number is always digits.
    if not str(pr_number).isdigit():
        print(f"Error: PR number must be a positive integer (got: {pr_number})")
        sys.exit(1)

    diff_content = get_pr_diff(pr_number, repo)
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
