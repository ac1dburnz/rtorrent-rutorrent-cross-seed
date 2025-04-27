import requests
import re
import os

repo = "Novik/ruTorrent"
try:
    token = os.environ.get('GITHUB_TOKEN')
    headers = {'Authorization': f'token {token}'} if token else {}

    # Get latest release
    releases_url = f"https://api.github.com/repos/{repo}/releases/latest"
    release_response = requests.get(releases_url, headers=headers)
    release_response.raise_for_status()
    latest_release = release_response.json()
    
    tag_name = latest_release["tag_name"]
    version = re.search(r'v(\d+\.\d+\.\d+)', tag_name).group(1)

    # Get commit SHA
    tags_url = f"https://api.github.com/repos/{repo}/git/refs/tags/{tag_name}"
    tag_response = requests.get(tags_url, headers=headers)
    tag_response.raise_for_status()
    latest_sha = tag_response.json()["object"]["sha"]

    print(f"Latest version: {version}")
    print(f"Latest commit SHA: {latest_sha}")

    # Update Dockerfile
    base_dir = os.environ.get("BASE_DIR")
    dockerfile_path = os.path.join(base_dir, "Dockerfile")  # Corrected path

    with open(dockerfile_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("# Novik/ruTorrent"):
            lines[i] = f'# Novik/ruTorrent {version}\n'
        if line.startswith("ARG RUTORRENT_VERSION="):
            lines[i] = f'ARG RUTORRENT_VERSION={latest_sha}\n'

    with open(dockerfile_path, "w") as f:
        f.writelines(lines)

    print("Successfully updated Dockerfile")

except Exception as e:
    print(f"Error: {str(e)}")
    exit(1)
