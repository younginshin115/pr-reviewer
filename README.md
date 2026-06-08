# PR Reviewer

AI-powered automated GitHub Pull Request code review tool. Supports both Cursor IDE and Claude Code.

## Prerequisites

- [GitHub CLI (`gh`)](https://cli.github.com/) - Install and authenticate with `gh auth login`
- [Python 3.x](https://www.python.org/)

## Setup

AI rules are automatically applied — no configuration needed:

- **Cursor**: `.cursor/github-pr-review.mdc`
- **Claude Code**: `.claude/commands/review-pr.md`

## Usage

### Cursor

```
123번 PR 리뷰해줘
Review PR #123
```

### Claude Code

```
/review-pr 123
```

AI automatically fetches the PR diff, analyzes the code, and posts review comments to GitHub.

### Changing Review Language

Review comments are written in Korean by default. To change the language:

- **Cursor**: `123번 PR 영어로 리뷰해줘` / `Review PR #123 in English`
- **Claude Code**: `/review-pr 123 --lang English`

## Project Structure

```
pr-reviewer/
├── .claude/commands/
│   └── review-pr.md              # Claude Code review command
├── .cursor/
│   └── github-pr-review.mdc      # Cursor AI review rules
├── pr-review-tools/
│   ├── fetch_pr_diff.py           # Fetch PR diff
│   ├── gh-pr-review.sh            # Post a full review (summary + inline comments)
│   └── gh-pr-reply.sh             # Reply to an existing comment thread
└── README.md
```
