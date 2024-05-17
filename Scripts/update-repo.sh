#!/bin/bash


#  Generate a branch name with current date and time
branch_name="branch_$(date +'%Y%m%d%H%M%S')" 

# Go to directory
cd "$BASE_DIR/rtorrent-rutorrent-cross-seed/Scripts"

# Ensure on main branch before creating new one  
git checkout main
git pull origin main

# Create and switch to new branch
git checkout -b "$branch_name"


# Run catalog update script  
python3 "$BASE_DIR/rtorrent-rutorrent-cross-seed/Scripts/rutorrent-auto-update.py"
#python3 "$BASE_DIR/rtorrent-rutorrent-cross-seed/Scripts/rtorrent-auto-update.py"


# Commit changes  
git add --all :/
git commit -m "Automatically generated changes on $branch_name"

# Push changes 
git push origin "$branch_name"

# Create PR
repo="ac1dburnz/rtorrent-rutorrent-cross-seed"
title="Automatically generated changes on $branch_name"
body="This pull request is automatically generated." 

pr_response=$(curl -X POST -H "Authorization: token $github_token" \
  -d '{"title":"'"$title"'","body":"'"$body"'","head":"'"$branch_name"'","base":"main"}' \
  "https://api.github.com/repos/$repo/pulls")

pr_number=$(echo $pr_response | jq '.number')

# Set PR to squash merge 
curl -X PATCH -H "Authorization: token $github_token" \
  -d '{"merge_method":"squash"}' \
  "https://api.github.com/repos/$repo/pulls/$pr_number"

# Merge PR
curl -X PUT -H "Authorization: token $github_token" \
  "https://api.github.com/repos/$repo/pulls/$pr_number/merge"

echo "PR merged successfully"
