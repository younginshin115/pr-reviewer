# PR Reviewer

A lightweight GitHub Pull Request review skill. No repo indexing, no review bot,
no extra account, seat, or token — it runs inside the coding agent you already
use, reads only as much code as a finding requires, and posts back actionable
comments in a single review.

Works across Claude Code, Cursor, and Codex CLI from one shared skill.

## Prerequisites

- [GitHub CLI (`gh`)](https://cli.github.com/) — install and authenticate with `gh auth login`
- [Python 3.x](https://www.python.org/)

## Install

Install the skill for your tool with `gh skill` or with `npx skills` — both place it
where your tool looks for skills. Replace `<AGENT>` with the value for your tool from
the table below:

```
# Using the GitHub CLI
gh skill install younginshin115/pr-reviewer review-pr --agent <AGENT> --scope user

# ...or using npx
npx skills add younginshin115/pr-reviewer --agent <AGENT> --global
```

| Tool          | `<AGENT>`     | Invoke               |
| ------------- | ------------- | -------------------- |
| Claude Code   | `claude-code` | `/review-pr 123`     |
| Cursor (2.4+) | `cursor`      | `/review-pr`         |
| Codex CLI     | `codex`       | `$review-pr`         |

In any tool you can also just ask: `Review PR #123`.

### Claude Code plugin (alternative)

Claude Code can instead install it as a plugin, which bundles the skill and tracks
updates through a marketplace:

```
/plugin marketplace add younginshin115/pr-reviewer
/plugin install pr-reviewer@pr-reviewer
```

Invoked this way, the command is namespaced: `/pr-reviewer:review-pr 123`.

## Review Language

Review comments are written in the language you're currently working in. To get a
review in a specific language, just ask in that language (e.g.
`Review PR #123 in English`).

## Project Structure

```
pr-reviewer/
├── skills/review-pr/               # The skill (Claude, Cursor, Codex)
│   ├── SKILL.md                    #   entry point the agent reads first
│   ├── references/
│   │   └── workflow.md             #   the review steps the agent follows
│   └── scripts/                    #   scripts the agent runs (via gh)
│       ├── fetch_pr_diff.py         #     fetch the PR diff, numbered for commenting
│       ├── gh-pr-review.sh          #     post the review (summary + inline comments)
│       └── gh-pr-reply.sh           #     reply in an existing comment thread
├── .claude-plugin/                 # Claude Code packaging
│   ├── plugin.json                 #   plugin manifest
│   └── marketplace.json            #   marketplace catalog
├── tests/
│   └── test_fetch_pr_diff.py       # tests for parse_diff
└── README.md
```

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Youngin Shin
