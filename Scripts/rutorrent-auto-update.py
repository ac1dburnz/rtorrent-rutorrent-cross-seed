#!/usr/bin/env python3
import os
import re
import requests

repo = "Novik/ruTorrent"
token = os.getenv("GITHUB_TOKEN")
headers = {"Accept": "application/vnd.github.v3+json"}
if token:
    headers["Authorization"] = f"token {token}"

workspace = os.getenv("GITHUB_WORKSPACE", os.getcwd())
dockerfile_path = os.path.join(workspace, "Dockerfile")

try:
    # Latest release
    rel = requests.get(f"https://api.github.com/repos/{repo}/releases/latest", headers=headers)
    rel.raise_for_status()
    tag = rel.json()["tag_name"]
    version = re.search(r"v(\d+\.\d+\.\d+)", tag).group(1)

    # Tag SHA
    ref = requests.get(f"https://api.github.com/repos/{repo}/git/refs/tags/{tag}", headers=headers)
    ref.raise_for_status()
    latest_sha = ref.json()["object"]["sha"]

    # Patch Dockerfile
    lines = open(dockerfile_path).read().splitlines(True)
    with open(dockerfile_path, 'w') as f:
        for line in lines:
            if line.startswith("# Novik/ruTorrent"):
                f.write(f"# Novik/ruTorrent {version}\n")
            elif line.startswith("ARG RUTORRENT_VERSION="):
                f.write(f"ARG RUTORRENT_VERSION={latest_sha}\n")
            else:
                f.write(line)

    print(f"ruTorrent updated to {version}, SHA {latest_sha}")
except Exception as e:
    print(f"Error in rutorrent-auto-update: {e}")
    raise
