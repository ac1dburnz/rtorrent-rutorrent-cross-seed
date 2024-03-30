import os
import re
import requests

print("Fetching latest commit SHA for repo")
repo = "Novik/ruTorrent"

response = requests.get(f"https://api.github.com/repos/{repo}/commits")
commits = response.json()
latest_commit = commits[0]
latest_sha = latest_commit["sha"]  

# Extract version
version = re.search(r'v(\d+\.\d+\.\d+)', latest_commit['commit']['message']).group(1)

print(f"Latest version: {version}")
print(f"Latest commit SHA: {latest_sha}")

print("Updating Dockerfile with latest version and commit SHA")

base_dir = os.environ.get("BASE_DIR")
dockerfile_path = os.path.join(base_dir, "rtorrent-rutorrent-cross-seed", "Dockerfile")

with open(dockerfile_path, "r") as f:
  lines = f.readlines()

for i, line in enumerate(lines):
  if line.startswith("#") and repo in line:
    lines[i] = f'# {repo} {version}\n'
    print(f"Updated comment: {lines[i]}")
    
  if line.startswith("ARG RUTORRENT_VERSION="):
    lines[i] = f'ARG RUTORRENT_VERSION={latest_sha}\n'
    print(f"Updated line: {lines[i]}")
    
with open(dockerfile_path, "w") as f:
  f.writelines(lines)
  
print("Dockerfile updated")
