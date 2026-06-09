# PR Reviewer

AI-powered automated GitHub Pull Request code review. Works across Claude Code,
Cursor, and Codex CLI from a single shared skill.

## Prerequisites

- [GitHub CLI (`gh`)](https://cli.github.com/) — install and authenticate with `gh auth login`
- [Python 3.x](https://www.python.org/)

## Usage

### Claude Code

Install as a plugin via the self-hosted marketplace:

```
/plugin marketplace add younginshin115/pr-reviewer
/plugin install pr-reviewer@pr-reviewer
```

Then review a PR from any project — invoke the skill or just ask:

```
/pr-reviewer:review-pr 123
Review PR #123
```

### Cursor & Codex CLI

Install the skill once into your user skills directory so it's available in every
project (the skill is self-contained — scripts and procedure travel with it):

```
cp -r .agents/skills/review-pr ~/.agents/skills/review-pr
```

Then, in any project, invoke it or just ask:

- **Cursor** (2.4+): `/review-pr` or `Review PR #123`
- **Codex CLI**: `$review-pr` or `Review PR #123`

## Review Language

Review comments are written in the language you're currently working in — Codex and
Cursor follow the conversation language, and Claude Code follows its `language`
setting (`settings.json`). To get a review in a specific language, just ask in that
language (e.g. `Review PR #123 in English`).

## Project Structure

```
pr-reviewer/
├── .agents/skills/review-pr/       # The self-contained skill (Claude, Cursor, Codex)
│   ├── SKILL.md                    #   entry point: how to run a review
│   ├── references/
│   │   └── workflow.md             #   the detailed review procedure
│   └── scripts/                    #   helper scripts, run by the skill
│       ├── fetch_pr_diff.py         #     fetch PR diff, numbered for commenting
│       ├── gh-pr-review.sh          #     post a full review (summary + inline comments)
│       └── gh-pr-reply.sh           #     reply to an existing comment thread
├── .claude-plugin/                 # Claude Code packaging
│   ├── plugin.json                 #   points "skills" at ./.agents/skills
│   └── marketplace.json            #   self-hosted marketplace
├── tests/
│   └── test_fetch_pr_diff.py       # Unit tests for parse_diff
└── README.md
```
