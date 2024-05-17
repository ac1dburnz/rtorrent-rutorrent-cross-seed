import requests
import re
import os

repo = "stickz/rtorrent"

try:
    # Get the tags sorted by their creation date
    tags_url = f"https://api.github.com/repos/{repo}/git/refs/tags"
    tags_response = requests.get(tags_url)
    tags_response.raise_for_status()  # Raise an error for bad status codes
    tags_data = tags_response.json()

    # Sort the tags by their creation date (using ISO 8601 date format)
    sorted_tags = sorted(tags_data, key=lambda x: x["object"]["tagger"]["date"], reverse=True)

    # Extract the latest tag and its associated SHA
    latest_tag_data = sorted_tags[0]
    latest_tag_name = latest_tag_data["ref"].split("/")[-1]  # Extract the tag name from the full ref
    latest_sha = latest_tag_data["object"]["sha"]

    # Extract the version number from the tag name
    match = re.search(r'v(\d+)', latest_tag_name, re.IGNORECASE)
    if match:
        version = match.group(1)
    else:
        raise ValueError(f"Could not extract version from tag name: {latest_tag_name}")

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
        if line.startswith("ARG RTORRENT_STICKZ_VERSION="):
            arg_line_index = i

    if comment_line_index is not None:
        lines[comment_line_index] = f'# rTorrent stickz {version}\n'

    if arg_line_index is not None:
        lines[arg_line_index] = f'ARG RTORRENT_STICKZ_VERSION={latest_sha}\n'

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

