---
name: review-pr
description: Review a GitHub Pull Request and post the findings as inline comments via gh. Use when the user asks to review a PR (e.g. "review PR #123", "123번 PR 리뷰해줘").
---

# GitHub PR Review

Review a GitHub Pull Request and post the findings as a single review.

This skill's directory contains:
- `scripts/` — the helper scripts (`fetch_pr_diff.py`, `gh-pr-review.sh`, `gh-pr-reply.sh`)
- `references/workflow.md` — the detailed review procedure

## Instructions

1. Determine the PR number from the user's request. Write review comments in the
   language you are currently responding in (this follows the tool's language
   setting or the conversation language). If the user explicitly asks for a
   different language, use that instead.

2. Resolve this skill's directory as an absolute path and set `SKILL_DIR` to it —
   under Claude Code it is `${CLAUDE_SKILL_DIR}`; in Cursor and Codex it is the
   directory this `SKILL.md` was loaded from. The helper scripts live in
   `$SKILL_DIR/scripts` and must be run by absolute path, because the working
   directory is the user's project, not this skill's directory.

3. Read `$SKILL_DIR/references/workflow.md` and carry out that workflow end-to-end:
   fetch the diff, analyze it, compose the review JSON, and actually post it. Don't
   stop after composing the JSON — run the post step and confirm in chat that the
   review was posted.
