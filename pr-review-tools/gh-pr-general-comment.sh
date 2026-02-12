#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f "$(dirname "$0")/.env" ]; then
    # Use set -a to automatically export variables, then source the file
    set -a
    source "$(dirname "$0")/.env"
    set +a
fi

# Ensure required environment variables are set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is not set."
    echo "Please set it in your .env file:"
    echo "GITHUB_TOKEN=your_github_token_here"
    exit 1
fi

if [ -z "$PROJECT_ROOT" ]; then
    echo "Error: PROJECT_ROOT environment variable is not set."
    echo "Please set it in your .env file:"
    echo "PROJECT_ROOT=/path/to/your/project"
    exit 1
fi

# Check arguments
if [ "$1" != "pr" ] || [ "$2" != "comment" ]; then
    echo "Usage: $0 pr comment <PR_NUMBER> --comment -b <comment text>"
    exit 1
fi

# Parse arguments
PR_NUMBER=$3
shift 3

COMMENT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --comment)
            shift
            if [ "$1" != "-b" ]; then
                echo "Error: --comment flag must be followed by -b <comment text>"
                exit 1
            fi
            shift
            # Collect all remaining arguments as comment text
            COMMENT="$*"
            break
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$PR_NUMBER" ] || [ -z "$COMMENT" ]; then
    echo "Error: Missing required parameters."
    echo "Usage: $0 pr comment <PR_NUMBER> --comment -b <comment text>"
    exit 1
fi

# Get repository owner and name from git remote
REMOTE_URL=$(git config --get remote.origin.url)
if [[ "$REMOTE_URL" =~ github.com[:/]([^/]+)/([^/.]+) ]]; then
    OWNER="${BASH_REMATCH[1]}"
    REPO="${BASH_REMATCH[2]}"
else
    echo "Error: Could not determine repository owner and name from remote URL: $REMOTE_URL"
    exit 1
fi

echo "Repository: $OWNER/$REPO"
echo "PR Number: $PR_NUMBER"
echo "Comment: $COMMENT"
echo "Posting general comment to PR..."

# Add general comment using GitHub API
API_URL="https://api.github.com/repos/$OWNER/$REPO/issues/$PR_NUMBER/comments"

# Create JSON payload safely using jq
JSON_PAYLOAD=$(jq -n \
    --arg body "$COMMENT" \
    '{
        body: $body
    }')

RESPONSE=$(curl -L -s -o "$(dirname "$0")/response.json" -w "%{http_code}" \
    -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    -H "Content-Type: application/json" \
    "$API_URL" \
    -d "$JSON_PAYLOAD")

if [[ "$RESPONSE" -ne 201 ]]; then
    echo "Failed to add general comment. Check response.json for more details."
    exit 1
fi

echo "General comment posted successfully."
