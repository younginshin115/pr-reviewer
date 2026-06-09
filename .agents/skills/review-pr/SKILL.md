---
name: review-pr
description: Review a GitHub Pull Request and post the findings as inline comments via gh. Use when the user asks to review a PR (e.g. "review PR #123", "123번 PR 리뷰해줘").
---

# GitHub PR Review

Review a GitHub Pull Request and post the findings as a single review. This one
skill is shared across Claude Code (as a bundled plugin skill), Cursor, and Codex
CLI — they all read this file.

## Instructions

1. Determine the PR number from the user's request. Write review comments in the
   language you are currently responding in (this follows the tool's language
   setting or the conversation language). If the user explicitly asks for a
   different language, use that instead.

2. Resolve the base directory that holds the shared files:
   - If `${CLAUDE_PLUGIN_ROOT}` is set (Claude Code plugin), the base is
     `${CLAUDE_PLUGIN_ROOT}`.
   - Otherwise (Cursor / Codex) the base is this repository's root. When reviewing
     a PR from a different project, set the `PR_REVIEW_TOOLS` environment variable to
     your clone's `pr-review-tools/` directory.

   Then set `PR_REVIEW_TOOLS` to `<base>/pr-review-tools` (use `$PR_REVIEW_TOOLS` if
   it is already set), and locate the workflow at `<base>/REVIEW_WORKFLOW.md`.

3. Read `REVIEW_WORKFLOW.md` (at the base resolved above) and carry out that
   workflow end-to-end: fetch the diff, analyze it, compose the review JSON, and
   actually post it. Don't stop after composing the JSON — run the post step and
   confirm in chat that the review was posted.
