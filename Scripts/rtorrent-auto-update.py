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

# Determine paths relative to this script's location
script_dir = os.path.dirname(os.path.realpath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, os.pardir))
dockerfile_path = os.path.join(repo_root, "Dockerfile")

try:
    # Fetch latest commit SHA
    commits_url = f"https://api.github.com/repos/{repo}/commits"
    resp = requests.get(commits_url, headers=headers)
    resp.raise_for_status()
    latest_sha = resp.json()[0]["sha"]

    # Fetch latest release tag
    releases_url = f"https://api.github.com/repos/{repo}/releases/latest"
    resp = requests.get(releases_url, headers=headers)
    resp.raise_for_status()
    tag = resp.json().get("tag_name", "")
    match = re.search(r"v(\d+)", tag, re.IGNORECASE)
    version = match.group(1) if match else "Unknown"

    # Read and patch Dockerfile
    with open(dockerfile_path, 'r') as f:
        lines = f.readlines()

    with open(dockerfile_path, 'w') as f:
        for line in lines:
            if line.startswith("# rTorrent stickz"):
                f.write(f"# rTorrent stickz {version}\n")
            elif line.startswith("ARG RTORRENT_STICKZ_VERSION="):
                f.write(f"ARG RTORRENT_STICKZ_VERSION={latest_sha}\n")
            else:
                f.write(line)

    print(f"rTorrent updated to version {version}, SHA {latest_sha}")

except Exception as e:
    print(f"Error in rtorrent-auto-update: {e}")
    raise
