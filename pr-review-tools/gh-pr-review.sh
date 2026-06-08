#!/bin/bash
set -euo pipefail

# Posts a complete PR review (summary + inline comments) in a single request via
# the pulls/{pr}/reviews endpoint, so everything lands as one cohesive review
# with one notification instead of separate per-comment threads.
#
# Usage: gh-pr-review.sh <PR_NUMBER> <REVIEW_JSON_FILE>
#
# REVIEW_JSON_FILE shape:
#   {
#     "body": "overall summary",
#     "comments": [
#       {"path": "file.py", "line": 10, "side": "RIGHT", "body": "..."}
#     ]
#   }
# - "comments" is optional; omit it (or pass an empty list) for an
#   approval/summary-only review.
# - "side" defaults to RIGHT; use LEFT to target a removed line.
# The review is always submitted with event=COMMENT, never an actual approval.

USAGE="Usage: $0 <PR_NUMBER> <REVIEW_JSON_FILE>"
PR_NUMBER="${1:-}"
REVIEW_FILE="${2:-}"

if [ -z "$PR_NUMBER" ] || [ -z "$REVIEW_FILE" ]; then
    echo "$USAGE"
    exit 1
fi

if ! [[ "$PR_NUMBER" =~ ^[0-9]+$ ]]; then
    echo "Error: PR number must be a positive integer (got: $PR_NUMBER)"
    exit 1
fi

if [ ! -f "$REVIEW_FILE" ]; then
    echo "Error: review file not found: $REVIEW_FILE"
    exit 1
fi

# Validate and normalize the payload with python3: force event=COMMENT, check
# each comment's fields, and default side to RIGHT. Errors go to stderr and
# abort before any API call.
PAYLOAD=$(python3 - "$REVIEW_FILE" <<'PY'
import json, sys

with open(sys.argv[1]) as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError as e:
        sys.exit(f"Error: invalid JSON in review file: {e}")

if not isinstance(data, dict):
    sys.exit("Error: review JSON must be an object")

body = data.get("body", "")
if not isinstance(body, str):
    sys.exit("Error: 'body' must be a string")

comments = data.get("comments", [])
if not isinstance(comments, list):
    sys.exit("Error: 'comments' must be a list")

out = {"event": "COMMENT", "body": body}
norm = []
for i, c in enumerate(comments):
    if not isinstance(c, dict):
        sys.exit(f"Error: comments[{i}] must be an object")
    for key in ("path", "line", "body"):
        if key not in c:
            sys.exit(f"Error: comments[{i}] missing required field '{key}'")
    side = c.get("side", "RIGHT")
    if side not in ("LEFT", "RIGHT"):
        sys.exit(f"Error: comments[{i}].side must be LEFT or RIGHT (got: {side})")
    try:
        line = int(c["line"])
    except (TypeError, ValueError):
        sys.exit(f"Error: comments[{i}].line must be an integer (got: {c['line']!r})")
    norm.append({"path": c["path"], "line": line, "side": side, "body": c["body"]})

if norm:
    out["comments"] = norm
if not body and not norm:
    sys.exit("Error: review needs a body or at least one comment")

print(f"Inline comments: {len(norm)}", file=sys.stderr)
json.dump(out, sys.stdout)
PY
) || exit 1

echo "PR Number: $PR_NUMBER"

# Post the review. gh substitutes {owner}/{repo} from the current repo and reads
# the JSON body from stdin via --input -.
if echo "$PAYLOAD" | gh api --method POST "repos/{owner}/{repo}/pulls/$PR_NUMBER/reviews" --input - >/dev/null; then
    echo "Review posted successfully."
else
    echo "Failed to post review."
    exit 1
fi
