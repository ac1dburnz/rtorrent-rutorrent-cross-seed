#!/bin/bash

# Dynamically determine the repository root directory
BASE_DIR=$(git rev-parse --show-toplevel)
if [ -z "$BASE_DIR" ]; then
  echo "Error: Unable to determine the repository root. Ensure this script is run inside a Git repository."
  exit 1
fi

# Set the correct default branch name (replace 'main' with your actual branch name if different)
DEFAULT_BRANCH="main"  # Update this if your default branch has a different name

# Generate a branch name with the current date and time
branch_name="branch_$(date +'%Y%m%d%H%M%S')"

# Navigate to the Scripts directory
cd "$BASE_DIR/Scripts" || { echo "Error: Scripts directory not found in $BASE_DIR"; exit 1; }

# Ensure on the default branch before creating a new one
git checkout "$DEFAULT_BRANCH" || { echo "Error: Failed to checkout $DEFAULT_BRANCH branch"; exit 1; }
git pull origin "$DEFAULT_BRANCH" || { echo "Error: Failed to pull latest changes from $DEFAULT_BRANCH"; exit 1; }

# Create and switch to a new branch
git checkout -b "$branch_name" || { echo "Error: Failed to create and switch to branch $branch_name"; exit 1; }

# Run update scripts
python3 ./rutorrent-auto-update.py || { echo "Error: Failed to run rutorrent-auto-update.py"; exit 1; }
python3 ./rtorrent-auto-update.py || { echo "Error: Failed to run rtorrent-auto-update.py"; exit 1; }

# Commit changes
git add --all || { echo "Error: Failed to stage changes"; exit 1; }
git commit -m "Automatically generated changes on $branch_name" || { echo "Error: Failed to commit changes"; exit 1; }

# Push changes
git push origin "$branch_name" || { echo "Error: Failed to push changes to branch $branch_name"; exit 1; }

# Create a pull request
repo="ac1dburnz/rtorrent-rutorrent-cross-seed"
title="Automatically generated changes on $branch_name"
body="This pull request is automatically generated."

pr_response=$(curl -X POST -H "Authorization: token $github_token" \
  -d '{"title":"'"$title"'","body":"'"$body"'","head":"'"$branch_name"'","base":"'"$DEFAULT_BRANCH"'"}' \
  "https://api.github.com/repos/$repo/pulls") || { echo "Error: Failed to create pull request"; exit 1; }

pr_number=$(echo "$pr_response" | jq '.number')
if [ -z "$pr_number" ] || [ "$pr_number" == "null" ]; then
  echo "Error: Failed to retrieve pull request number"
  exit 1
fi

# Set PR to squash merge
curl -X PATCH -H "Authorization: token $github_token" \
  -d '{"merge_method":"squash"}' \
  "https://api.github.com/repos/$repo/pulls/$pr_number" || { echo "Error: Failed to set squash merge method"; exit 1; }

# Merge PR
curl -X PUT -H "Authorization: token $github_token" \
  "https://api.github.com/repos/$repo/pulls/$pr_number/merge" || { echo "Error: Failed to merge pull request"; exit 1; }

echo "PR merged successfully"
