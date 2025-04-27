import requests
import re
import os

repo = "stickz/rtorrent"
try:
    token = os.environ.get('GITHUB_TOKEN')
    headers = {'Authorization': f'token {token}'} if token else {}

    # Get latest commit
    commits_url = f"https://api.github.com/repos/{repo}/commits"
    commits_response = requests.get(commits_url, headers=headers)
    commits_response.raise_for_status()
    latest_commit = commits_response.json()[0]
    latest_sha = latest_commit["sha"]

    # Get latest release
    releases_url = f"https://api.github.com/repos/{repo}/releases/latest"
    release_response = requests.get(releases_url, headers=headers)
    release_response.raise_for_status()
    latest_release = release_response.json()
    
    tag_name = latest_release.get("tag_name", "No Tag")
    match = re.search(r'v(\d+)', tag_name, re.IGNORECASE)
    version = match.group(1) if match else "Unknown"

    print(f"Latest version: {version}")
    print(f"Latest commit SHA: {latest_sha}")

    # Update Dockerfile
    base_dir = os.environ.get("BASE_DIR")
    if not base_dir:
        raise ValueError("BASE_DIR environment variable is not set")
        
    dockerfile_path = os.path.join(base_dir, "Dockerfile")  # Corrected path
    
    if not os.path.exists(dockerfile_path):
        raise FileNotFoundError(f"Dockerfile not found at: {dockerfile_path}")

    with open(dockerfile_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("# rTorrent stickz"):
            lines[i] = f'# rTorrent stickz {version}\n'
        if line.startswith("ARG RTORRENT_STICKZ_VERSION="):
            lines[i] = f'ARG RTORRENT_STICKZ_VERSION={latest_sha}\n'

    with open(dockerfile_path, "w") as f:
        f.writelines(lines)

    print("Successfully updated Dockerfile")

except Exception as e:
    print(f"Error: {str(e)}")
    exit(1)
