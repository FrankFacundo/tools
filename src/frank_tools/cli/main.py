"""Central CLI for Frank tools."""

from __future__ import annotations

import argparse
from typing import Callable, Dict

from frank_tools.audio.m4b_splitter import M4BSplitter, parse_chapter_file
from frank_tools.download.drive import download_file_from_link
from frank_tools.translate.google_free import GoogleTranslate


def _add_drive_download(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("drive-download", help="Download a file from Google Drive")
    parser.add_argument("-l", "--link", required=True, help="Google Drive share link or ID")
    parser.add_argument("-o", "--output", default=".", help="Directory to save the download")
    parser.set_defaults(func=_handle_drive_download)


def _add_translate(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("translate", help="Translate text")
    parser.add_argument("--text", required=True, help="Text to translate")
    parser.add_argument("--sl", default="auto", help="Source language")
    parser.add_argument("--tl", default="en", help="Target language")
    parser.set_defaults(func=_handle_translate)


def _add_m4b_split(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("m4b-split", help="Split an M4B using a chapter manifest")
    parser.add_argument("--input", required=True, help="Input .m4b file")
    parser.add_argument("--chapters", required=True, help="Chapter manifest file")
    parser.add_argument("--output", default="output", help="Directory for chapter files")
    parser.set_defaults(func=_handle_m4b_split)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="frank-tools", description="Frank tools CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    _add_drive_download(subparsers)
    _add_translate(subparsers)
    _add_m4b_split(subparsers)
    return parser


def _handle_drive_download(args: argparse.Namespace) -> None:
    dest = download_file_from_link(args.link, output_dir=args.output)
    print(f"Downloaded to: {dest}")


def _handle_translate(args: argparse.Namespace) -> None:
    translator = GoogleTranslate()
    result = translator.translate(args.text, sl=args.sl, tl=args.tl)
    print(result["translation"])


def _handle_m4b_split(args: argparse.Namespace) -> None:
    manifest = parse_chapter_file(args.chapters)
    splitter = M4BSplitter.from_manifest(args.input, manifest, output_dir=args.output)
    outputs = splitter.split()
    for out in outputs:
        print(out)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler: Callable[[argparse.Namespace], None] = args.func
    handler(args)


if __name__ == "__main__":
    main()
