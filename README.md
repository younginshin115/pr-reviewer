# PR Reviewer

AI-powered automated GitHub Pull Request code review. Works across Claude Code,
Cursor, and Codex CLI from a single shared skill.

## Prerequisites

- [GitHub CLI (`gh`)](https://cli.github.com/) — install and authenticate with `gh auth login`
- [Python 3.x](https://www.python.org/)

## Usage

### Claude Code

Install as a plugin via the self-hosted marketplace (the plugin bundles the skill
and its scripts, so it works from any project):

```
/plugin marketplace add younginshin115/pr-reviewer
/plugin install pr-reviewer@pr-reviewer
```

Then review a PR from any project — invoke the skill or just ask:

```
/pr-reviewer:review-pr 123
Review PR #123
```

To test a local checkout instead of the GitHub repo, point the marketplace at your
clone: `/plugin marketplace add /path/to/pr-reviewer`.

### Cursor

The skill at `.agents/skills/review-pr/` is discovered automatically when this repo
is your project (Cursor 2.4+). Invoke it with `/review-pr` or just ask:

```
Review PR #123
```

### Codex CLI

The skill at `.agents/skills/review-pr/` is discovered automatically when this repo
is your project. Invoke it with `$review-pr` or just ask:

```
Review PR #123
```

**Using Cursor or Codex from another project:** copy `.agents/skills/review-pr/` to
`~/.agents/skills/review-pr/` and set the `PR_REVIEW_TOOLS` environment variable to
your clone's `pr-review-tools/` directory (the skill also needs access to
`REVIEW_WORKFLOW.md` from your clone).

## Review Language

Review comments are written in the language you're currently working in — Codex and
Cursor follow the conversation language, and Claude Code follows its `language`
setting (`settings.json`). To get a review in a specific language, just ask in that
language (e.g. `Review PR #123 in English`).

## Project Structure

```
pr-reviewer/
├── .agents/skills/review-pr/
│   └── SKILL.md                  # The shared skill (Claude Code, Cursor, Codex)
├── REVIEW_WORKFLOW.md            # Single source of truth: the review procedure
├── pr-review-tools/              # Helper scripts (shared by all tools)
│   ├── fetch_pr_diff.py           # Fetch PR diff, numbered for commenting
│   ├── gh-pr-review.sh            # Post a full review (summary + inline comments)
│   └── gh-pr-reply.sh             # Reply to an existing comment thread
├── .claude-plugin/               # Claude Code packaging
│   ├── plugin.json               #   points "skills" at ./.agents/skills
│   └── marketplace.json          #   self-hosted marketplace
├── tests/
│   └── test_fetch_pr_diff.py     # Unit tests for parse_diff
└── README.md
```
