# GitHub PR Review

Review GitHub Pull Request and post comments.

Usage: `/review-pr <PR_NUMBER> [--lang <language>]`

- `--lang`: Review comment language (default: Korean)
- Example: `/review-pr 123 --lang English`

## Workflow

1. **Get PR diff**: Fetch the PR diff using `fetch_pr_diff.py`
2. **Analyze code**: Identify issues in the diff
3. **Post comments**: Post review comments to GitHub using the scripts

## Instructions

Parse `$ARGUMENTS` to extract the PR number and optional `--lang` flag. If `--lang` is not provided, default to Korean.

You are an experienced senior software engineer reviewing the PR.

### Step 1: Fetch PR Diff

Run the following command to get the PR diff:

```bash
python3 pr-review-tools/fetch_pr_diff.py
```

Note: The script automatically detects the PR from the current branch. If you need to review a specific PR, use `gh pr diff $ARGUMENTS` directly.

### Step 2: Analyze the Diff

Review the code changes with these principles:

**What to comment on:**
- Actual bugs or errors
- Security vulnerabilities
- Critical code quality issues
- Logic errors

**What NOT to comment on:**
- Code style or formatting
- Adding comments or documentation
- Minor improvements or suggestions
- Positive feedback or praise

**Review scope:**
- Only review new code (lines with `+`)
- Write actionable comments only
- Do not make assumptions about code outside the diff

### Step 3: Post Comments

For each issue found, use this script to post a line-specific comment:

```bash
pr-review-tools/gh-pr-comment.sh pr review $ARGUMENTS --comment -b "<review comment in Korean>" --path <FILE_PATH> --line <LINE_NUMBER>
```

### Step 4: Handle Approval

If no issues are found, post an approval comment:

```bash
pr-review-tools/gh-pr-general-comment.sh pr comment $ARGUMENTS --comment -b "No issues found. Approved."
```

### Comment Writing Rules

- **Write all comments in the language specified by `--lang` (default: Korean)**
- Use markdown formatting
- Do not use code blocks in review comments
- Ignore end-of-file newline issues
- Each comment must be actionable

### Important Notes

- Actually execute the scripts - do not just return JSON
- Confirm in chat that all comments have been posted
- This posts comments only, not an actual PR approval action
