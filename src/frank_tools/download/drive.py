"""Google Drive downloader utility."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Optional

import requests
from tqdm import tqdm

CONFIRM_TOKEN_PREFIX = "download_warning"
DOWNLOAD_URL = "https://docs.google.com/uc?export=download"
CHUNK_SIZE = 32768


def extract_file_id(file_input: str) -> str:
    """
    Extracts the file ID from a Google Drive URL or returns the ID as-is.

    Example URL: https://drive.google.com/file/d/<id>/view?usp=sharing
    """
    if file_input.startswith("http"):
        match = re.search(r"/d/([^/]+)", file_input)
        if match:
            return match.group(1)
        raise ValueError("Invalid Google Drive link format. Could not extract file ID.")
    return file_input


def get_confirm_token(response: requests.Response) -> Optional[str]:
    """Return the confirmation token if present in the response cookies."""
    for key, value in response.cookies.items():
        if key.startswith(CONFIRM_TOKEN_PREFIX):
            return value
    return None


def get_file_name(response: requests.Response, default: str = "downloaded_file") -> str:
    """Extract file name from the Content-Disposition header."""
    cd = response.headers.get("Content-Disposition")
    if cd:
        fname = re.findall('filename="(.+)"', cd)
        if fname:
            return fname[0]
    return default


def save_response_content(response: requests.Response, destination: Path) -> Path:
    """Stream response content into a file."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as f:
        for chunk in tqdm(response.iter_content(CHUNK_SIZE), desc="Downloading", unit="chunk"):
            if chunk:
                f.write(chunk)
    return destination


def download_file_by_id(file_id: str, session: Optional[requests.Session] = None, output_dir: Path | str = ".") -> Path:
    """
    Download a Google Drive file by ID and return the destination path.
    """
    output_dir = Path(output_dir)
    session = session or requests.Session()

    response = session.get(DOWNLOAD_URL, params={"id": file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        response = session.get(DOWNLOAD_URL, params={"id": file_id, "confirm": token}, stream=True)

    destination = output_dir / get_file_name(response)
    return save_response_content(response, destination)


def download_file_from_link(link: str, output_dir: Path | str = ".") -> Path:
    """
    Download a file from a Google Drive link or file ID.

    Returns the path to the downloaded file.
    """
    file_id = extract_file_id(link)
    return download_file_by_id(file_id, output_dir=output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a file from Google Drive using its shareable link. "
        "The file name is automatically extracted from the response headers."
    )
    parser.add_argument("-l", "--link", type=str, required=True, help="Google Drive shareable link or file ID")
    parser.add_argument("-o", "--output", type=str, default=".", help="Directory to save the file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    destination = download_file_from_link(args.link, output_dir=args.output)
    print(f"Downloaded to: {destination}")


if __name__ == "__main__":
    main()
