import requests
import re 
import os

repo = "Novik/ruTorrent"

releases_url = f"https://api.github.com/repos/{repo}/releases"
commits_url = f"https://api.github.com/repos/{repo}/commits"

release_response = requests.get(releases_url)
latest_release = release_response.json()[0]

tag_name = latest_release["tag_name"] 
version = re.search(r'v(\d+\.\d+\.\d+)', tag_name).group(1)

commit_response = requests.get(commits_url)
latest_commit = commit_response.json()[0]
latest_sha = latest_commit["sha"]

print(f"Latest version: {version}")
print(f"Latest commit SHA: {latest_sha}")

base_dir = os.environ.get("BASE_DIR")
dockerfile_path = os.path.join(base_dir, "rtorrent-rutorrent-cross-seed", "Dockerfile")

with open(dockerfile_path, "r") as f:
  lines = f.readlines()
  
comment_line_index = None  
arg_line_index = None

for i, line in enumerate(lines):
  if line.startswith("# Novik/ruTorrent"): 
    comment_line_index = i
    
  if line.startswith("ARG RUTORRENT_VERSION="):
    arg_line_index = i
    
if comment_line_index is not None:
  lines[comment_line_index] = f'# Novik/ruTorrent {version}\n' 

if arg_line_index is not None:
  lines[arg_line_index] = f'ARG RUTORRENT_VERSION={latest_sha}\n'
  
with open(dockerfile_path, "w") as f:
  f.writelines(lines)
  
print("Dockerfile updated")
