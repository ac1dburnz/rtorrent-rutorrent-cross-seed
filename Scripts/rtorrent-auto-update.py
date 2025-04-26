#!/usr/bin/env python3
import os
import re
#!/usr/bin/env python3
import os
import re
import requests

repo = "stickz/rtorrent"
token = os.getenv("GITHUB_TOKEN")
headers = {"Accept": "application/vnd.github.v3+json"}
if token:
    headers["Authorization"] = f"token {token}"

# GITHUB_WORKSPACE is already the repo root; Dockerfile sits here
workspace = os.getenv("GITHUB_WORKSPACE", os.getcwd())
dockerfile_path = os.path.join(workspace, "Dockerfile")

try:
    # Latest commit SHA
    commits = requests.get(f"https://api.github.com/repos/{repo}/commits", headers=headers)
    commits.raise_for_status()
    latest_sha = commits.json()[0]["sha"]

    # Latest release tag => version
    rel = requests.get(f"https://api.github.com/repos/{repo}/releases/latest", headers=headers)
    rel.raise_for_status()
    tag = rel.json().get("tag_name", "")
    m = re.search(r"v(\d+)", tag, re.IGNORECASE)
    version = m.group(1) if m else "Unknown"

    # Patch Dockerfile
    lines = open(dockerfile_path).read().splitlines(True)
    with open(dockerfile_path, 'w') as f:
        for line in lines:
            if line.startswith("# rTorrent stickz"):
                f.write(f"# rTorrent stickz {version}\n")
            elif line.startswith("ARG RTORRENT_STICKZ_VERSION="):
                f.write(f"ARG RTORRENT_STICKZ_VERSION={latest_sha}\n")
            else:
                f.write(line)

    print(f"rTorrent updated to {version}, SHA {latest_sha}")
except Exception as e:
    print(f"Error in rtorrent-auto-update: {e}")
    raise
