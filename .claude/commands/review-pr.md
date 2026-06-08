# GitHub PR Review

Review GitHub Pull Request and post comments.

Usage: `/review-pr <PR_NUMBER> [--lang <language>]`

- `--lang`: Review comment language (default: Korean)
- Example: `/review-pr 123 --lang English`

## Workflow

1. **Get PR diff**: Fetch the PR diff using `fetch_pr_diff.py`
2. **Analyze code**: Identify issues in the diff
3. **Post the review**: Post all findings as a single review using `gh-pr-review.sh`

## Instructions

Parse `$ARGUMENTS` to extract the PR number and optional `--lang` flag. If `--lang` is not provided, default to Korean.

You are an experienced senior software engineer reviewing the PR.

### Step 1: Fetch PR Diff

Run the following command to get the PR diff:

```bash
python3 pr-review-tools/fetch_pr_diff.py <PR_NUMBER>
```

Note: Pass the PR number explicitly. If omitted, the script falls back to detecting the PR from the current branch.

Each output line is prefixed with the line number to use as a comment's `line`:
- `+` added lines use the new-file number (`side: RIGHT`, the default)
- `-` removed lines use the old-file number (`side: LEFT`)
- ` ` context lines are numbered with the new-file line

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

### Step 3: Compose the Review

Collect all findings into a single review JSON file. Each finding becomes one
inline comment anchored to a `path` + `line` (+ `side`); the `body` is an
overall summary. Write it to a temp file, e.g. `/tmp/review.json`:

```json
{
  "body": "<overall summary in the review language>",
  "comments": [
    {"path": "<FILE_PATH>", "line": <LINE_NUMBER>, "side": "RIGHT", "body": "<comment>"},
    {"path": "<FILE_PATH>", "line": <LINE_NUMBER>, "side": "LEFT", "body": "<comment on a removed line>"}
  ]
}
```

- Take `line` from the Step 1 output; use `side: LEFT` for removed (`-`) lines, `RIGHT` (default) for added (`+`) lines.
- For an approval (no issues found), set `body` to `"No issues found. Approved."` and omit `comments`.

### Step 4: Post the Review

Post the whole review in one request:

```bash
pr-review-tools/gh-pr-review.sh <PR_NUMBER> /tmp/review.json
```

This submits a single cohesive review (one notification) with `event=COMMENT` —
it never performs an actual approval action.

### Step 5: Re-review After Fixes

When the user indicates fixes have been pushed (e.g., "수정됐어", "고쳤어", "fixed"):

1. **Fetch latest**: `git fetch origin <branch>` and pull new commits
2. **Review fix commits**: Verify the previously-flagged issues are resolved
3. **Second-pass review**: Re-scan the rest of the PR for any issues missed earlier
4. **Decide**:
   - No issues → post an approval review via Steps 3–4 (body only, no comments)
   - Issues found → compose and post a new review via Steps 3–4

To reply within an existing comment thread (e.g. confirming a fix in-thread),
use `gh-pr-reply.sh`. Find the comment id first:

```bash
gh api "repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments" --jq '.[] | {id, path, line, body}'
pr-review-tools/gh-pr-reply.sh <PR_NUMBER> <COMMENT_ID> -b "<reply>"
```

### Comment Writing Rules

- **Write all comments in the language specified by `--lang` (default: Korean)**
- Use markdown formatting
- Do not use code blocks in review comments
- Ignore end-of-file newline issues
- Each comment must be actionable

### Important Notes

- Don't stop after composing the review JSON — actually run `gh-pr-review.sh` to post it
- Confirm in chat that the review has been posted
- This posts comments only, not an actual PR approval action
