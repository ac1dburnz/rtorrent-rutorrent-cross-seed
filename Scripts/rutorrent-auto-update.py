#!/usr/bin/env python3
import os
import re
import requests

# Configuration
repo = "Novik/ruTorrent"

token = os.getenv("GITHUB_TOKEN")
headers = {"Accept": "application/vnd.github.v3+json"}
if token:
    headers["Authorization"] = f"token {token}"

# Locate Dockerfile by walking up
def find_dockerfile(start_dir):
    current = start_dir
    while True:
        candidate = os.path.join(current, "Dockerfile")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    raise FileNotFoundError("Dockerfile not found in any parent directory.")

script_dir = os.path.dirname(os.path.realpath(__file__))
dockerfile_path = find_dockerfile(script_dir)

try:
    # Get latest release
    release = requests.get(f"https://api.github.com/repos/{repo}/releases/latest", headers=headers)
    release.raise_for_status()
    tag = release.json()["tag_name"]
    version = re.search(r"v(\d+\.\d+\.\d+)", tag).group(1)

    # Get tag SHA
    ref = requests.get(f"https://api.github.com/repos/{repo}/git/refs/tags/{tag}", headers=headers)
    ref.raise_for_status()
    latest_sha = ref.json()["object"]["sha"]

    # Patch Dockerfile
    with open(dockerfile_path) as f:
        lines = f.readlines()
    with open(dockerfile_path, 'w') as f:
        for line in lines:
            if line.startswith("# Novik/ruTorrent"):
                f.write(f"# Novik/ruTorrent {version}\n")
            elif line.startswith("ARG RUTORRENT_VERSION="):
                f.write(f"ARG RUTORRENT_VERSION={latest_sha}\n")
            else:
                f.write(line)

    print(f"ruTorrent updated: version={version}, sha={latest_sha}")
except Exception as e:
    print(f"Error in rutorrent-auto-update: {e}")
    raise
