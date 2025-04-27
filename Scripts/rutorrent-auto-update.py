import requests
import re
import os
import sys

REPO = "Novik/ruTorrent"
DOCKERFILE_PATH = "Dockerfile"

def main():
    try:
        headers = {"Authorization": f"token {os.environ['GITHUB_TOKEN']}"} if 'GITHUB_TOKEN' in os.environ else {}
        
        # Get latest release
        release = requests.get(f"https://api.github.com/repos/{REPO}/releases/latest", headers=headers).json()
        tag_name = release['tag_name']
        version = re.search(r'v(\d+\.\d+\.\d+)', tag_name).group(1)
        
        # Get commit SHA for the tag
        tag_ref = requests.get(f"https://api.github.com/repos/{REPO}/git/ref/tags/{tag_name}", headers=headers).json()
        commit_sha = tag_ref['object']['sha'][:7]

        # Update Dockerfile
        with open(DOCKERFILE_PATH, 'r') as f:
            content = f.read()

        new_content = re.sub(
            r'(ARG RUTORRENT_VERSION=).+',
            f'\\g<1>{commit_sha}  # Version: {version}',
            content
        )

        if content != new_content:
            with open(DOCKERFILE_PATH, 'w') as f:
                f.write(new_content)
            print("Updated ruTorrent version")
        else:
            print("No ruTorrent updates found")

    except Exception as e:
        print(f"Error checking ruTorrent: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
