#!/bin/bash

base_dir= "$BASE_DIR"

# Generate a branch name with current date and time
branch_name="branch_$(date +'%Y%m%d%H%M%S')" 

# Go to directory
cd "$BASE_DIR/rtorrent-rutorrent-cross-seed"

# Ensure on main branch before creating new one  
git checkout main
git pull origin main

# Create and switch to new branch
git checkout -b "$branch_name"


# Run catalog fix script
python3 "$BASE_DIR/rtorrent-rutorrent-cross-seed/Scripts/rutorrent-auto-update.py"

# Commit changes  
git add --all :/
git commit -m "Automatically generated changes on $branch_name"

# Push changes 
git push origin "$branch_name"

# Create PR
pr_data='{
   "title": "Automated update",
   "body": "Automated PR",
   "head": "new-branch",
   "base": "main"  
}'

pr_response=$(curl -H "Authorization: token $github_token" -X POST -d "$pr_data" https://api.github.com/repos/$REPO/pulls)

pr_number=$(echo $pr_response | jq '.number')

# Set squash merge
curl -H "Authorization: token $github_token" -X PATCH -d '{"merge_method":"squash"}' https://api.github.com/repos/$REPO/pulls/$pr_number

# Merge PR
curl -H "Authorization: token $github_token" -X PUT https://api.github.com/repos/$REPO/pulls/$pr_number/merge


echo "PR merged successfully"
