import os
import re
import requests

repo = "Novik/ruTorrent"  

releases_url = f"https://api.github.com/repos/{repo}/releases"
commits_url = f"https://api.github.com/repos/{repo}/commits"

release_response = requests.get(releases_url)
latest_release = release_response.json()[0]

tag_name = latest_release["tag_name"]
version = re.search(r'v(\d+\.\d+\.\d+)', tag_name).group(1)

commit_response = requests.get(commits_url)
latest_commit = commit_response.json()[0]
sha = latest_commit["sha"] 

print(f"Latest version: {version}")
print(f"Latest SHA: {sha}")

base_dir = os.environ.get("BASE_DIR") 
dockerfile_path = os.path.join(base_dir, "rtorrent-rutorrent-cross-seed", "Dockerfile")

with open(dockerfile_path, "r") as f:

  lines = f.readlines()
  
  rutorrent_line = None
  
  for i, line in enumerate(lines):
  
    if "Novik/ruTorrent" in line:
      rutorrent_line = i
      
  if rutorrent_line is not None:
    lines[rutorrent_line] = f'# Novik/ruTorrent {version}\n'

  with open(dockerfile_path, "w") as f:
    f.writelines(lines)
    
print("Dockerfile updated")
