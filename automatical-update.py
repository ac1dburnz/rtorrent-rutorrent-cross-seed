import os
import datetime
import subprocess
import requests
import json

# Config
BASE_DIR = "/Users/ac1dburn/Documents/GitHub/rtorrent-rutorrent-cross-seed" 
REPO = "ac1dburnz/ac1ds-catalog"
BRANCH_PREFIX = "auto-update-"
COMMIT_MSG = "Automated update"
PR_TITLE = "Automated update"
PR_BODY = "Automatically generated PR"
GITHUB_TOKEN = os.environ['github_token']

# Generate branch name
now = datetime.datetime.now()
branch_name = f"{BRANCH_PREFIX}{now.strftime('%Y%m%d%H%M%S')}"

# Switch to repo and pull latest changes
os.chdir(BASE_DIR)
subprocess.run(["git", "checkout", "main"])
subprocess.run(["git", "pull", "origin", "main"])

# Create branch and make commit
subprocess.run(["git", "checkout", "-b", branch_name])
subprocess.run(["git", "add", "--all"])
subprocess.run(["git", "commit", "-m", COMMIT_MSG]) 

# Push branch
subprocess.run(["git", "push", "origin", branch_name])

# Create PR
data = {
   "title": PR_TITLE,
   "body": PR_BODY,
   "head": branch_name,
   "base": "main"
}
url = f"https://api.github.com/repos/{REPO}/pulls"
headers = {"Authorization": f"token {GITHUB_TOKEN}"}
response = requests.post(url, json=data, headers=headers)
pr_number = response.json()["number"]

# Set squash merge
url = f"https://api.github.com/repos/{REPO}/pulls/{pr_number}" 
data = {"merge_method": "squash"}
requests.patch(url, json=data, headers=headers)

# Merge PR
url = f"https://api.github.com/repos/{REPO}/pulls/{pr_number}/merge"
requests.put(url, headers=headers) 

print("PR merged successfully!")
