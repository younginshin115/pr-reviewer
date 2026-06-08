#!/bin/bash
set -euo pipefail

# Replies to an existing review-comment thread on a PR, for back-and-forth after
# the initial review (e.g. confirming a fix or answering a question in-thread).
#
# Usage: gh-pr-reply.sh <PR_NUMBER> <COMMENT_ID> -b <reply text>
#
# COMMENT_ID is the id of the review comment to reply to. List them with:
#   gh api "repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments" --jq '.[] | {id, path, line, original_line, body}'
# (After new commits a comment's line may be null; its line is then in original_line.)

USAGE="Usage: $0 <PR_NUMBER> <COMMENT_ID> -b <reply text>"
PR_NUMBER="${1:-}"
COMMENT_ID="${2:-}"
FLAG="${3:-}"
BODY="${4:-}"

if [ -z "$PR_NUMBER" ] || [ -z "$COMMENT_ID" ] || [ "$FLAG" != "-b" ] || [ -z "$BODY" ]; then
    echo "$USAGE"
    exit 1
fi

if ! [[ "$PR_NUMBER" =~ ^[0-9]+$ ]]; then
    echo "Error: PR number must be a positive integer (got: $PR_NUMBER)"
    exit 1
fi

if ! [[ "$COMMENT_ID" =~ ^[0-9]+$ ]]; then
    echo "Error: comment ID must be a positive integer (got: $COMMENT_ID)"
    exit 1
fi

echo "PR Number: $PR_NUMBER"
echo "Reply to comment: $COMMENT_ID"
echo "Reply: $BODY"

# gh substitutes {owner}/{repo} from the current repo.
if gh api --method POST "repos/{owner}/{repo}/pulls/$PR_NUMBER/comments/$COMMENT_ID/replies" \
    -f body="$BODY" >/dev/null; then
    echo "Reply posted successfully."
else
    echo "Failed to post reply."
    exit 1
fi
