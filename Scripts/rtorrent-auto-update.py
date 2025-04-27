import requests
import re
import os
import sys

repo = "stickz/rtorrent"

try:
    headers = {}
    if 'GITHUB_TOKEN' in os.environ:
        headers = {'Authorization': f'token {os.environ["GITHUB_TOKEN"]}'}

    # Get latest commit
    commits_response = requests.get(f"https://api.github.com/repos/{repo}/commits", headers=headers)
    commits_response.raise_for_status()
    latest_sha = commits_response.json()[0]["sha"]  # Keep full SHA

    # Get latest release
    release_response = requests.get(f"https://api.github.com/repos/{repo}/releases/latest", headers=headers)
    release_response.raise_for_status()
    tag_name = release_response.json().get("tag_name", "")
    
    # Extract version from tag (v7.2-0.9.8-0.13.8 -> 7.2)
    version_match = re.search(r'v(\d+\.\d+)', tag_name)
    if not version_match:
        raise ValueError(f"Invalid tag format: {tag_name}")
    version = version_match.group(1)

    print(f"Latest rTorrent version: {version}")
    print(f"Latest commit SHA: {latest_sha}")

    # Update Dockerfile
    dockerfile_path = os.path.join(os.environ["BASE_DIR"], "Dockerfile")
    
    with open(dockerfile_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("# rTorrent stickz"):
            lines[i] = f'# rTorrent stickz {version}\n'
        if line.startswith("ARG RTORRENT_STICKZ_VERSION="):
            lines[i] = f'ARG RTORRENT_STICKZ_VERSION={latest_sha}\n'  # Full SHA

    with open(dockerfile_path, "w") as f:
        f.writelines(lines)

    print("Dockerfile updated successfully")

except Exception as e:
    print(f"Error updating rTorrent: {str(e)}")
    sys.exit(1)


