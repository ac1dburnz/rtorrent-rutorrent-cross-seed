import os
import re
import requests 

repo = "Novik/ruTorrent"

releases_url = f"https://api.github.com/repos/{repo}/releases"
commits_url = f"https://api.github.com/repos/{repo}/commits"

# Get latest release for version
release_response = requests.get(releases_url)
latest_release = release_response.json()[0]

tag_name = latest_release["tag_name"]  
version = re.search(r'v(\d+\.\d+\.\d+)', tag_name).group(1)

# Get latest commit for SHA
commit_response = requests.get(commits_url)  
latest_commit = commit_response.json()[0]
sha = latest_commit["sha"]

print(f"Latest version: {version}")
print(f"Latest SHA: {sha}")

base_dir = os.environ.get("BASE_DIR")
dockerfile_path = os.path.join(base_dir, "rtorrent-rutorrent-cross-seed", "Dockerfile")

with open(dockerfile_path, "r") as f:

  lines = f.readlines()

  for i, line in enumerate(lines):

    if line.startswith("#"):
      lines[i] = f'# {repo} {version}\n' 

    if line.startswith("ARG RUTORRENT_VERSION="):
      lines[i] = f'ARG RUTORRENT_VERSION={sha}\n'

with open(dockerfile_path, "w") as f:
  f.writelines(lines)
  
print("Dockerfile updated")
