import re
import subprocess
import argparse
from urllib.parse import urlparse

def get_repo():
    """Fetches the GitHub repository details from the current branch."""
    result = subprocess.run("git config --get remote.origin.url", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error fetching repository details (exit code: {result.returncode}):")
        print(f"Command: git config --get remote.origin.url")
        print(f"Error: {result.stderr}")
        print("Please ensure you are in a git repository with a remote origin configured.")
        exit(1)
    repo_url = result.stdout.strip()
    
    # Parse URL safely using urllib.parse
    parsed_url = urlparse(repo_url)
    
    # Handle both SSH and HTTPS URLs
    if parsed_url.scheme == 'ssh' or ':' in parsed_url.path:
        # SSH format: git@github.com:owner/repo.git
        path = parsed_url.path.lstrip('/')
        if ':' in path:
            owner, repo = path.split(':', 1)
        else:
            owner, repo = path.split('/', 1)
    else:
        # HTTPS format: https://github.com/owner/repo.git
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) >= 2:
            owner, repo = path_parts[0], path_parts[1]
        else:
            print("Error: Invalid repository URL format")
            exit(1)
    
    # Remove .git extension if present
    repo = repo.replace('.git', '')
    
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
    current_file = None
    current_hunk = None

    for line in diff_text.splitlines():
        file_match = re.match(r'^diff --git a/(.+) b/(.+)', line)
        if file_match:
            if current_file:
                result.append("\n".join(current_file))
            current_file = [f"## File: '{file_match.group(2)}'"]
            current_hunk = None  # Reset current hunk when a new file starts
            continue

        hunk_match = re.match(r'^@@.*@@', line)
        if hunk_match:
            if current_hunk:
                result.append("\n".join(current_hunk))
            current_hunk = ["\n@@ ... @@", "__new hunk__"]
            continue

        if current_hunk is None:
            current_hunk = []  # Ensure hunk is initialized

        if line.startswith('+') and not line.startswith('+++'):
            current_hunk.append(f"{line[1:]} +new code line added in the PR")
        elif line.startswith('-') and not line.startswith('---'):
            current_hunk.append(f"{line[1:]} -old code line removed in the PR")
        else:
            current_hunk.append(line)

    if current_hunk:
        result.append("\n".join(current_hunk))

    if current_file:
        result.append("\n".join(current_file))

    return "\n".join(result)

if __name__ == "__main__":
    repo = get_repo()
    pr_number = get_pr_number()
    
    diff_content = get_pr_diff(pr_number, repo)
    parsed_diff = parse_diff(diff_content)
    print(parsed_diff)
