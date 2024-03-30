import os
import re 
import requests

print("Fetching latest release...")

repo = "Novik/ruTorrent"
releases_url = f"https://api.github.com/repos/{repo}/releases"

response = requests.get(releases_url)
latest_release = response.json()[0]

tag_name = latest_release["tag_name"]
version = re.search(r'v(\d+\.\d+\.\d+)', tag_name).group(1)

print(f"Latest version: {version}")

# Rest of script to update Dockerfile...

base_dir = os.environ.get("BASE_DIR")
dockerfile_path = os.path.join(base_dir, "rtorrent-rutorrent-cross-seed", "Dockerfile")

with open(dockerfile_path, "r") as f:
  lines = f.readlines()

for i, line in enumerate(lines):
  if line.startswith("#") and repo in line:
    lines[i] = f'# {repo} {version}\n'

  if line.startswith("ARG RUTORRENT_VERSION="): 
    lines[i] = f'ARG RUTORRENT_VERSION={version}\n'
    
with open(dockerfile_path, "w") as f:
  f.writelines(lines)

print("Dockerfile updated")
