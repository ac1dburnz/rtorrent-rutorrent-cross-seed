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

# Determine paths relative to this script's location
script_dir = os.path.dirname(os.path.realpath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, os.pardir))
dockerfile_path = os.path.join(repo_root, "Dockerfile")

try:
    # Fetch latest release info
    rel_url = f"https://api.github.com/repos/{repo}/releases/latest"
    resp = requests.get(rel_url, headers=headers)
    resp.raise_for_status()
    tag = resp.json()["tag_name"]
    version = re.search(r"v(\d+\.\d+\.\d+)", tag).group(1)

    # Fetch commit SHA for tag
    ref_url = f"https://api.github.com/repos/{repo}/git/refs/tags/{tag}"
    resp = requests.get(ref_url, headers=headers)
    resp.raise_for_status()
    latest_sha = resp.json()["object"]["sha"]

    # Read and patch Dockerfile
    with open(dockerfile_path, 'r') as f:
        lines = f.readlines()

    with open(dockerfile_path, 'w') as f:
        for line in lines:
            if line.startswith("# Novik/ruTorrent"):
                f.write(f"# Novik/ruTorrent {version}\n")
            elif line.startswith("ARG RUTORRENT_VERSION="):
                f.write(f"ARG RUTORRENT_VERSION={latest_sha}\n")
            else:
                f.write(line)

    print(f"ruTorrent updated to version {version}, SHA {latest_sha}")

except Exception as e:
    print(f"Error in rutorrent-auto-update: {e}")
    raise
