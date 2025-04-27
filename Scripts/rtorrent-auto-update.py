import requests
import re
import os
import sys

REPO = "stickz/rtorrent"
DOCKERFILE_PATH = "Dockerfile"

def main():
    try:
        headers = {"Authorization": f"token {os.environ['GITHUB_TOKEN']}"} if 'GITHUB_TOKEN' in os.environ else {}
        
        # Get latest release
        release = requests.get(f"https://api.github.com/repos/{REPO}/releases/latest", headers=headers).json()
        tag_name = release.get('tag_name', '')
        version = re.search(r'v(\d+)', tag_name).group(1) if tag_name else "0"
        
        # Get latest commit
        commit = requests.get(f"https://api.github.com/repos/{REPO}/commits", headers=headers).json()[0]
        commit_sha = commit['sha'][:7]

        # Update Dockerfile
        with open(DOCKERFILE_PATH, 'r') as f:
            content = f.read()

        new_content = re.sub(
            r'(ARG RTORRENT_STICKZ_VERSION=).+',
            f'\\g<1>{commit_sha}  # Version: {version}',
            content
        )

        if content != new_content:
            with open(DOCKERFILE_PATH, 'w') as f:
                f.write(new_content)
            print("Updated rTorrent version")
        else:
            print("No rTorrent updates found")

    except Exception as e:
        print(f"Error checking rTorrent: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
