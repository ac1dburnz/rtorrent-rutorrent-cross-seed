import requests
import re
import os

repo = "stickz/rtorrent"

try:
    # Get the latest release information
    releases_url = f"https://api.github.com/repos/{repo}/releases/latest"
    release_response = requests.get(releases_url)
    release_response.raise_for_status()  # Raise an error for bad status codes
    latest_release = release_response.json()

    # Extract the tag name and version number
    tag_name = latest_release["tag_name"]
    print(f"Fetched tag name: {tag_name}")  # Debugging output

    # Use a regular expression to extract the version number from the tag name
    match = re.search(r'v(\d+)', tag_name, re.IGNORECASE)
    if match:
        version = match.group(1)
    else:
        raise ValueError(f"Could not extract version from tag name: {tag_name}")

    # Get the commit SHA associated with the latest release tag
    tags_url = f"https://api.github.com/repos/{repo}/git/refs/tags/{tag_name}"
    tag_response = requests.get(tags_url)
    tag_response.raise_for_status()  # Raise an error for bad status codes
    tag_data = tag_response.json()
    latest_sha = tag_data["object"]["sha"]

    print(f"Latest version: {version}")
    print(f"Latest commit SHA: {latest_sha}")

    # Update the Dockerfile
    base_dir = os.environ.get("BASE_DIR")
    if not base_dir:
        raise ValueError("BASE_DIR environment variable is not set")

    dockerfile_path = os.path.join(base_dir, "rtorrent-rutorrent-cross-seed", "Dockerfile")
    if not os.path.exists(dockerfile_path):
        raise FileNotFoundError(f"Dockerfile not found at path: {dockerfile_path}")

    with open(dockerfile_path, "r") as f:
        lines = f.readlines()

    comment_line_index = None
    arg_line_index = None

    for i, line in enumerate(lines):
        if line.startswith("# rTorrent stickz"):
            comment_line_index = i
        if line.startswith("ARG RTORRENT_VERSION="):
            arg_line_index = i

    if comment_line_index is not None:
        lines[comment_line_index] = f'# rTorrent stickz {version}\n'

    if arg_line_index is not None:
        lines[arg_line_index] = f'ARG RTORRENT_VERSION={latest_sha}\n'

    with open(dockerfile_path, "w") as f:
        f.writelines(lines)

    print("Dockerfile updated")

except requests.exceptions.RequestException as e:
    print(f"HTTP Request failed: {e}")
except ValueError as e:
    print(f"Value Error: {e}")
except FileNotFoundError as e:
    print(f"File Not Found Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
