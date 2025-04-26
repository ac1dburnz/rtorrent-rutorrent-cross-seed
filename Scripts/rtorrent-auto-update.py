#!/usr/bin/env python3
import os
import re
import requests

# Configuration
repo = "stickz/rtorrent"
token = os.getenv("GITHUB_TOKEN")
headers = {"Accept": "application/vnd.github.v3+json"}
if token:
    headers["Authorization"] = f"token {token}"

# Paths
github_workspace = os.getenv("GITHUB_WORKSPACE", os.getcwd())
dockerfile = os.path.join(github_workspace, "rtorrent-rutorrent-cross-seed", "Dockerfile")

try:
    # Fetch latest commit
    commits_url = f"https://api.github.com/repos/{repo}/commits"
    resp = requests.get(commits_url, headers=headers)
    resp.raise_for_status()
    latest_sha = resp.json()[0]["sha"]

    # Fetch latest release tag
    release_url = f"https://api.github.com/repos/{repo}/releases/latest"
    resp = requests.get(release_url, headers=headers)
    resp.raise_for_status()
    tag = resp.json().get("tag_name", "")
    version = re.search(r"v(\d+)", tag, re.IGNORECASE)
    version = version.group(1) if version else "Unknown"

    # Update Dockerfile
    with open(dockerfile, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("# rTorrent stickz"):
            lines[i] = f"# rTorrent stickz {version}\n"
        if line.startswith("ARG RTORRENT_STICKZ_VERSION="):
            lines[i] = f"ARG RTORRENT_STICKZ_VERSION={latest_sha}\n"

    with open(dockerfile, 'w') as f:
        f.writelines(lines)

    print(f"rTorrent updated to version {version}, SHA {latest_sha}")

except Exception as e:
    print(f"Error in rtorrent-auto-update: {e}")
    raise
