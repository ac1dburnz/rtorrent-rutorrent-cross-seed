#!/usr/bin/env python3
import os
import re
import requests

# Configuration
repo = "stickz/rtorrent"

# Auth headers
token = os.getenv("GITHUB_TOKEN")
headers = {"Accept": "application/vnd.github.v3+json"}
if token:
    headers["Authorization"] = f"token {token}"

# Locate Dockerfile by walking up from this script
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
    # Get latest commit SHA
    commits = requests.get(f"https://api.github.com/repos/{repo}/commits", headers=headers)
    commits.raise_for_status()
    latest_sha = commits.json()[0]["sha"]

    # Get latest release tag
    release = requests.get(f"https://api.github.com/repos/{repo}/releases/latest", headers=headers)
    release.raise_for_status()
    tag = release.json().get("tag_name", "")
    match = re.search(r"v(\d+)", tag, re.IGNORECASE)
    version = match.group(1) if match else "Unknown"

    # Patch Dockerfile
    with open(dockerfile_path) as f:
        lines = f.readlines()
    with open(dockerfile_path, 'w') as f:
        for line in lines:
            if line.startswith("# rTorrent stickz"):
                f.write(f"# rTorrent stickz {version}\n")
            elif line.startswith("ARG RTORRENT_STICKZ_VERSION="):
                f.write(f"ARG RTORRENT_STICKZ_VERSION={latest_sha}\n")
            else:
                f.write(line)

    print(f"rTorrent updated: version={version}, sha={latest_sha}")
except Exception as e:
    print(f"Error in rtorrent-auto-update: {e}")
    raise
