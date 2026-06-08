# PR Reviewer

AI-powered automated GitHub Pull Request code review tool. Supports both Cursor IDE and Claude Code.

## Prerequisites

- [GitHub CLI (`gh`)](https://cli.github.com/) - Install and authenticate with `gh auth login`
- [Python 3.x](https://www.python.org/)
- [jq](https://jqlang.github.io/jq/) - JSON parsing
- [curl](https://curl.se/)
- GitHub Personal Access Token (`repo` scope)

## Setup

1. Create `pr-review-tools/.env` file (see `.env.example`)

```bash
GITHUB_TOKEN=your_github_token_here
```

2. AI rules are automatically applied
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
│   ├── gh-pr-comment.sh           # Post line-specific comments
│   ├── .env                       # Environment variables (gitignored)
│   └── .env.example
└── README.md
```
