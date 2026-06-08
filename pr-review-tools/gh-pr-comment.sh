#!/bin/bash

# Posts a line-specific review comment via the GitHub CLI (`gh api`).
# gh handles authentication and resolves the {owner}/{repo} placeholders from
# the current repository, so no PAT or remote-URL parsing is needed here.

# Check arguments
USAGE="Usage: $0 pr review <PR_NUMBER> --comment -b <review comment> --path <FILE_PATH> --line <LINE_NUMBER> [--side LEFT|RIGHT] [--commit-id <SHA>]"
if [ "$1" != "pr" ] || [ "$2" != "review" ]; then
    echo "$USAGE"
    exit 1
fi

# Parse arguments
PR_NUMBER=$3
shift 3

COMMENT=""
FILE_PATH=""
LINE_NUMBER=""
SIDE="RIGHT"
COMMIT_ID=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --comment)
            shift
            if [ "$1" != "-b" ]; then
                echo "Error: --comment flag must be followed by -b <review comment>"
                exit 1
            fi
            shift
            COMMENT="$1"
            ;;
        --path)
            shift
            FILE_PATH="$1"
            ;;
        --line)
            shift
            LINE_NUMBER="$1"
            ;;
        --side)
            shift
            SIDE="$1"
            ;;
        --commit-id)
            shift
            COMMIT_ID="$1"
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
    shift
done

# Validate required parameters
if [ -z "$PR_NUMBER" ] || [ -z "$COMMENT" ] || [ -z "$FILE_PATH" ] || [ -z "$LINE_NUMBER" ]; then
    echo "Error: Missing required parameters."
    echo "$USAGE"
    exit 1
fi

# Validate side value (LEFT targets removed lines, RIGHT targets added lines)
if [ "$SIDE" != "LEFT" ] && [ "$SIDE" != "RIGHT" ]; then
    echo "Error: --side must be either LEFT or RIGHT (got: $SIDE)"
    exit 1
fi

# Validate the line number so a malformed value fails clearly instead of
# producing an invalid API request later.
if ! [[ "$LINE_NUMBER" =~ ^[0-9]+$ ]]; then
    echo "Error: --line must be a positive integer (got: $LINE_NUMBER)"
    exit 1
fi

# Resolve the commit to attach the comment to, unless one was supplied via
# --commit-id. Passing --commit-id lets callers fetch the SHA once and reuse it
# across multiple comments instead of querying the PR for every comment.
if [ -z "$COMMIT_ID" ]; then
    echo "Resolving head commit..."
    COMMIT_ID=$(gh pr view "$PR_NUMBER" --json headRefOid -q .headRefOid)
fi

if [ -z "$COMMIT_ID" ]; then
    echo "Error: Could not resolve the head commit for PR #$PR_NUMBER"
    exit 1
fi

echo "PR Number: $PR_NUMBER"
echo "File Path: $FILE_PATH"
echo "Line Number: $LINE_NUMBER"
echo "Side: $SIDE"
echo "Commit ID: $COMMIT_ID"
echo "Comment: $COMMENT"

# Post the review comment. gh substitutes {owner}/{repo} from the current repo
# and sends -F line as a number, so no manual JSON assembly is needed.
if gh api --method POST "repos/{owner}/{repo}/pulls/$PR_NUMBER/comments" \
    -f body="$COMMENT" \
    -f commit_id="$COMMIT_ID" \
    -f path="$FILE_PATH" \
    -F line="$LINE_NUMBER" \
    -f side="$SIDE" >/dev/null; then
    echo "Review comment added successfully."
else
    echo "Failed to add review comment."
    exit 1
fi
