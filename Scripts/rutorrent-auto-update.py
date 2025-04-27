import requests
import re
import os
import sys

repo = "Novik/ruTorrent"

try:
    headers = {}
    if 'GITHUB_TOKEN' in os.environ:
        headers = {'Authorization': f'token {os.environ["GITHUB_TOKEN"]}'}

    # Get latest release
    release_response = requests.get(f"https://api.github.com/repos/{repo}/releases/latest", headers=headers)
    release_response.raise_for_status()
    tag_name = release_response.json()["tag_name"]
    
    # Extract version (v5.2.0 -> 5.2)
    version_match = re.search(r'v(\d+\.\d+)', tag_name)
    if not version_match:
        raise ValueError(f"Invalid tag format: {tag_name}")
    version = version_match.group(1)

    # Get commit SHA for tag
    tag_response = requests.get(f"https://api.github.com/repos/{repo}/git/ref/tags/{tag_name}", headers=headers)
    tag_response.raise_for_status()
    latest_sha = tag_response.json()["object"]["sha"]  # Full SHA

    print(f"Latest ruTorrent version: {version}")
    print(f"Associated commit SHA: {latest_sha}")

    # Update Dockerfile
    dockerfile_path = os.path.join(os.environ["BASE_DIR"], "Dockerfile")
    
    with open(dockerfile_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("# Novik/ruTorrent"):
            lines[i] = f'# Novik/ruTorrent {version}\n'
        if line.startswith("ARG RUTORRENT_VERSION="):
            lines[i] = f'ARG RUTORRENT_VERSION={latest_sha}\n'  # Full SHA

    with open(dockerfile_path, "w") as f:
        f.writelines(lines)

    print("Dockerfile updated successfully")

except Exception as e:
    print(f"Error updating ruTorrent: {str(e)}")
    sys.exit(1)
