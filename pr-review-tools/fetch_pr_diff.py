import re
import subprocess
import argparse

def get_repo():
    """Fetches the GitHub repository (owner/repo) from the current branch's remote."""
    result = subprocess.run("git config --get remote.origin.url", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error fetching repository details (exit code: {result.returncode}):")
        print(f"Command: git config --get remote.origin.url")
        print(f"Error: {result.stderr}")
        print("Please ensure you are in a git repository with a remote origin configured.")
        exit(1)
    repo_url = result.stdout.strip()

    # Handles both SSH (git@github.com:owner/repo.git) and HTTPS (https://github.com/owner/repo.git)
    match = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', repo_url)
    if not match:
        print(f"Error: Could not parse owner/repo from remote URL: {repo_url}")
        exit(1)
    owner, repo = match.group(1), match.group(2)

    return f"{owner}/{repo}"

def get_pr_number():
    """Fetches the current PR number if available."""
    result = subprocess.run("gh pr view --json number --jq .number", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error fetching PR number (exit code: {result.returncode}):")
        print(f"Command: gh pr view --json number --jq .number")
        print(f"Error: {result.stderr}")
        print("Please ensure:")
        print("1. You are on a PR branch")
        print("2. GitHub CLI (gh) is installed and authenticated")
        print("3. You have access to the repository")
        exit(1)
    return result.stdout.strip()

def get_pr_diff(pr_number, repo):
    """Fetches the PR diff using GitHub CLI."""
    cmd = f"gh pr diff {pr_number} --repo {repo}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error fetching PR diff (exit code: {result.returncode}):")
        print(f"Command: {cmd}")
        print(f"Error: {result.stderr}")
        print("Please ensure:")
        print(f"1. PR #{pr_number} exists in repository {repo}")
        print("2. You have access to view the PR")
        print("3. GitHub CLI (gh) is authenticated")
        exit(1)
    return result.stdout

def parse_diff(diff_text):
    result = []
    in_hunk = False

    for line in diff_text.splitlines():
        file_match = re.match(r'^diff --git a/(.+) b/(.+)', line)
        if file_match:
            result.append(f"## File: '{file_match.group(2)}'")
            in_hunk = False  # Reset when a new file starts
            continue

        hunk_match = re.match(r'^@@.*@@', line)
        if hunk_match:
            result.append("\n@@ ... @@")
            result.append("__new hunk__")
            in_hunk = True
            continue

        # Skip diff metadata (index, mode, ---/+++ headers) before the first hunk
        if not in_hunk:
            continue

        if line.startswith('+') and not line.startswith('+++'):
            result.append(f"{line[1:]} +new code line added in the PR")
        elif line.startswith('-') and not line.startswith('---'):
            result.append(f"{line[1:]} -old code line removed in the PR")
        else:
            result.append(line)

    return "\n".join(result)

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

    diff_content = get_pr_diff(pr_number, repo)
    parsed_diff = parse_diff(diff_content)
    print(parsed_diff)
