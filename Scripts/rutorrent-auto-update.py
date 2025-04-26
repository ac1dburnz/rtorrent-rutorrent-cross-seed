#!/usr/bin/env python3
import os
import re
import requests

repo = "Novik/ruTorrent"
token = os.getenv("GITHUB_TOKEN")
headers = {"Accept": "application/vnd.github.v3+json"}
if token:
    headers["Authorization"] = f"token {token}"

github_workspace = os.getenv("GITHUB_WORKSPACE", os.getcwd())
dockerfile = os.path.join(github_workspace, "rtorrent-rutorrent-cross-seed", "Dockerfile")

try:
    # Fetch latest release info
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    tag = resp.json()["tag_name"]
    version = re.search(r"v(\d+\.\d+\.\d+)", tag).group(1)

    # Fetch SHA for the tag
    ref_url = f"https://api.github.com/repos/{repo}/git/refs/tags/{tag}"
    resp = requests.get(ref_url, headers=headers)
    resp.raise_for_status()
    latest_sha = resp.json()["object"]["sha"]

    # Update Dockerfile
    with open(dockerfile, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("# Novik/ruTorrent"):
            lines[i] = f"# Novik/ruTorrent {version}\n"
        if line.startswith("ARG RUTORRENT_VERSION="):
            lines[i] = f"ARG RUTORRENT_VERSION={latest_sha}\n"

    with open(dockerfile, 'w') as f:
        f.writelines(lines)

    print(f"ruTorrent updated to {version}, SHA {latest_sha}")

except Exception as e:
    print(f"Error in rutorrent-auto-update: {e}")
    raise
