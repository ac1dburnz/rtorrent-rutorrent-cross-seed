#!/bin/bash

# Set BASE_DIR dynamically
BASE_DIR=$(git rev-parse --show-toplevel)
cd "$BASE_DIR/Scripts" || exit 1

# Check for jq dependency
if ! command -v jq &> /dev/null; then
  echo "Error: jq is not installed."
  exit 1
fi

# Use GITHUB_TOKEN if github_token is not set
if [ -z "$github_token" ]; then
  github_token=$GITHUB_TOKEN
fi

# Generate a branch name with current date and time
branch_name="branch_$(date +'%Y%m%d%H%M%S')"

# Ensure on main branch before creating new one
git checkout main || exit 1
git pull origin main || exit 1

# Create and switch to new branch
git checkout -b "$branch_name" || exit 1

# Run Python scripts
python3 ./rutorrent-auto-update.py || exit 1
python3 ./rtorrent-auto-update.py || exit 1

# Configure Git user
git config user.email "github-actions-bot@users.noreply.github.com"
git config user.name "GitHub Actions Bot"

# Commit changes
git add --all :/ || exit 1
git commit -m "Automatically generated changes on $branch_name" || exit 1

# Push changes
git push origin "$branch_name" || exit 1

# Create Pull Request
repo="ac1dburnz/rtorrent-rutorrent-cross-seed"
title="Automatically generated changes on $branch_name"
body="This pull request is automatically generated."

pr_response=$(curl -X POST -H "Authorization: token $github_token" \
  -d '{"title":"'"$title"'","body":"'"$body"'","head":"'"$branch_name"'","base":"main"}' \
  "https://api.github.com/repos/$repo/pulls") || exit 1

pr_number=$(echo $pr_response | jq '.number')
if [ "$pr_number" == "null" ] || [ -z "$pr_number" ]; then
  echo "Error: Failed to create pull request."
  exit 1
fi

# Set PR to squash merge
curl -X PATCH -H "Authorization: token $github_token" \
  -d '{"merge_method":"squash"}' \
  "https://api.github.com/repos/$repo/pulls/$pr_number" || exit 1

# Merge PR
merge_response=$(curl -X PUT -H "Authorization: token $github_token" \
  "https://api.github.com/repos/$repo/pulls/$pr_number/merge")
if echo "$merge_response" | grep -q '"merged":true'; then
  echo "PR merged successfully"
else
  echo "Error: PR merge failed."
  exit 1
fi
