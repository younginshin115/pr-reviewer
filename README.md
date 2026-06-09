# PR Reviewer

AI-powered automated GitHub Pull Request code review. Works across Claude Code,
Cursor, and Codex CLI from a single shared skill.

## Prerequisites

- [GitHub CLI (`gh`)](https://cli.github.com/) — install and authenticate with `gh auth login`
- [Python 3.x](https://www.python.org/)

## Usage

### Claude Code

Install as a plugin via its marketplace:

```
/plugin marketplace add younginshin115/pr-reviewer
/plugin install pr-reviewer@pr-reviewer
```

Then review a PR from any project — invoke the skill or just ask:

```
/pr-reviewer:review-pr 123
Review PR #123
```

### Cursor

Install at user scope with the GitHub CLI, or with `npx skills` if you don't have it
(both place the skill in the directory Cursor expects):

```
gh skill install younginshin115/pr-reviewer review-pr --agent cursor --scope user
npx skills add younginshin115/pr-reviewer --agent cursor --global
```

Then, in any project (Cursor 2.4+), invoke it or just ask:

```
/review-pr
Review PR #123
```

### Codex CLI

Install at user scope with the GitHub CLI, or with `npx skills` if you don't have it:

```
gh skill install younginshin115/pr-reviewer review-pr --agent codex --scope user
npx skills add younginshin115/pr-reviewer --agent codex --global
```

Then, in any project, invoke it or just ask:

```
$review-pr
Review PR #123
```

## Review Language

Review comments are written in the language you're currently working in. To get a
review in a specific language, just ask in that language (e.g.
`Review PR #123 in English`).

## Project Structure

```
pr-reviewer/
├── skills/review-pr/               # The self-contained skill (Claude, Cursor, Codex)
│   ├── SKILL.md                    #   entry point: how to run a review
│   ├── references/
│   │   └── workflow.md             #   the detailed review procedure
│   └── scripts/                    #   helper scripts, run by the skill
│       ├── fetch_pr_diff.py         #     fetch PR diff, numbered for commenting
│       ├── gh-pr-review.sh          #     post a full review (summary + inline comments)
│       └── gh-pr-reply.sh           #     reply to an existing comment thread
├── .claude-plugin/                 # Claude Code packaging
│   ├── plugin.json                 #   plugin manifest
│   └── marketplace.json            #   marketplace catalog
├── tests/
│   └── test_fetch_pr_diff.py       # Unit tests for parse_diff
└── README.md
```
