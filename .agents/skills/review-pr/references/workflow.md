# PR Review Workflow

The detailed procedure for reviewing a GitHub Pull Request and posting the review.
`SKILL.md` (one directory up) points here so the procedure lives in one place.

You are an experienced senior software engineer reviewing the PR.

## Conventions

- `$PR_REVIEW_TOOLS` is the skill's `scripts/` directory, set by `SKILL.md`. Use it
  verbatim in the commands below (scripts are referenced by absolute path).
- `<PR_NUMBER>` is the pull request number. If it wasn't supplied, extract it from
  the user's request.

## Step 1: Fetch the PR diff

```bash
python3 "$PR_REVIEW_TOOLS/fetch_pr_diff.py" <PR_NUMBER>
```

If `<PR_NUMBER>` is omitted, the script falls back to detecting the PR from the
current branch.

Each output line is prefixed with the line number to use as a comment's `line`:

- `+` added lines use the new-file number (`side: RIGHT`, the default)
- `-` removed lines use the old-file number (`side: LEFT`)
- ` ` context lines are numbered with the new-file line

The text after `@@ ... @@` is the surrounding function/context for orientation only.

## Step 2: Analyze the diff

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
- Do not return comments that are even slightly similar to other existing comments

## Step 3: Compose the review

Collect all findings into a single review JSON file. Each finding becomes one
inline comment anchored to a `path` + `line` (+ `side`); the `body` is an overall
summary. Write it to a temp file, e.g. `/tmp/review.json`:

```json
{
  "body": "<overall summary in the review language>",
  "comments": [
    {"path": "<FILE_PATH>", "line": <LINE_NUMBER>, "side": "RIGHT", "body": "<comment>"},
    {"path": "<FILE_PATH>", "line": <LINE_NUMBER>, "side": "LEFT", "body": "<comment on a removed line>"}
  ]
}
```

- Take `line` from the Step 1 output; use `side: LEFT` for removed (`-`) lines,
  `RIGHT` (default) for added (`+`) lines.
- For an approval (no issues found), set `body` to `"No issues found. Approved."`
  and omit `comments`.

## Step 4: Post the review

Post the whole review in one request:

```bash
"$PR_REVIEW_TOOLS/gh-pr-review.sh" <PR_NUMBER> /tmp/review.json
```

This submits a single cohesive review (one notification) with `event=COMMENT` —
it never performs an actual approval action.

## Step 5: Re-review after fixes

When the user indicates fixes have been pushed (e.g., "수정됐어", "고쳤어", "fixed"):

1. **Fetch latest**: `git fetch origin <branch>` and pull new commits
2. **Review fix commits**: Verify the previously-flagged issues are resolved
3. **Second-pass review**: Re-scan the rest of the PR for any issues missed earlier
4. **Decide**:
   - No issues → post an approval review via Steps 3–4 (body only, no comments)
   - Issues found → compose and post a new review via Steps 3–4

To reply within an existing comment thread (e.g. confirming a fix in-thread), use
`gh-pr-reply.sh`. Find the comment id first:

```bash
gh api "repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments" --jq '.[] | {id, path, line, original_line, body}'
"$PR_REVIEW_TOOLS/gh-pr-reply.sh" <PR_NUMBER> <COMMENT_ID> -b "<reply>"
```

Note: after new commits are pushed, a comment's `line` may become `null` (its
position is outdated); its line is then in `original_line`. Match on `id` to reply.

## Comment writing rules

- **Language**: write all comments in the language you are currently responding in —
  this naturally follows the user's tool language setting or the conversation
  language. If the user explicitly asks for a different language, use that instead.
- Use markdown formatting
- Do not use code blocks in review comments
- Ignore end-of-file newline issues
- Each comment must be actionable

## Important notes

- Don't stop after composing the review JSON — actually run `gh-pr-review.sh` to post it
- Confirm in chat that the review has been posted
- This posts comments only, not an actual PR approval action
- Keep in mind you're only seeing part of the code — do not make assumptions about
  code outside the diff
