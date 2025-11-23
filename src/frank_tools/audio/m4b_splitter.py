"""Lightweight M4B splitter utilities."""

from __future__ import annotations

import argparse
import datetime
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

logger = logging.getLogger(__name__)


@dataclass
class Chapter:
    """
    MP4 Chapter with timings stored in seconds.
    """

    title: str
    start: float
    end: float
    num: int | None = None

    @classmethod
    def from_milliseconds(cls, title: str, start_ms: int, end_ms: int, num: int | None = None) -> "Chapter":
        return cls(title=title, start=round(start_ms / 1000.0, 3), end=round(end_ms / 1000.0, 3), num=num)

    def duration(self) -> float:
        if self.start is None or self.end is None:
            return 0.0
        return round(self.end - self.start, 3)

    def __str__(self) -> str:
        return f'<Chapter Title="{self.title}", Start={datetime.timedelta(seconds=self.start)}, End={datetime.timedelta(seconds=self.end)}, Duration={datetime.timedelta(seconds=self.duration())}>'


class M4BSplitter:
    """
    Simple ffmpeg-based chapter splitter for .m4b files.
    """

    def __init__(self, input_path: Path | str, chapters: Sequence[Chapter], output_dir: Path | str = "."):
        self.input_path = Path(input_path)
        self.chapters = list(chapters)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def build_ffmpeg_command(input_file: Path, output_file: Path, start: float, end: float) -> List[str]:
        """
        Build an ffmpeg command for extracting a single chapter.
        """
        return [
            "ffmpeg",
            "-y",
            "-i",
            str(input_file),
            "-ss",
            str(start),
            "-to",
            str(end),
            "-c",
            "copy",
            str(output_file),
        ]

    @classmethod
    def from_manifest(cls, input_path: Path | str, manifest: Iterable[tuple[str, float, float]], output_dir: Path | str = ".") -> "M4BSplitter":
        chapters = [Chapter(title=title, start=start, end=end, num=index + 1) for index, (title, start, end) in enumerate(manifest)]
        return cls(input_path=input_path, chapters=chapters, output_dir=output_dir)

    def split(self) -> List[Path]:
        """
        Split the input file into chapter files.
        """
        outputs: List[Path] = []
        for chapter in self.chapters:
            output_file = self._output_path_for_chapter(chapter)
            cmd = self.build_ffmpeg_command(self.input_path, output_file, chapter.start, chapter.end)
            logger.debug("Running command: %s", " ".join(cmd))
            self._run_command(cmd)
            outputs.append(output_file)
        return outputs

    def _output_path_for_chapter(self, chapter: Chapter) -> Path:
        safe_title = chapter.title.replace(" ", "_")
        prefix = f"{chapter.num:02d}_" if chapter.num is not None else ""
        return self.output_dir / f"{prefix}{safe_title}.m4a"

    def _run_command(self, cmd: Sequence[str]) -> None:
        subprocess.run(cmd, check=True, capture_output=True)


def parse_chapter_file(path: Path | str) -> List[tuple[str, float, float]]:
    """
    Parse a simple chapter manifest file where each line is:
    <start_seconds>,<end_seconds>,<title>
    """
    entries: List[tuple[str, float, float]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            start_str, end_str, title = stripped.split(",", 2)
            entries.append((title.strip(), float(start_str), float(end_str)))
    return entries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Split an M4B file into chapter segments using ffmpeg.")
    parser.add_argument("--input", type=str, required=True, help="Input .m4b file")
    parser.add_argument("--chapters", type=str, required=True, help="Path to chapter manifest (<start>,<end>,<title>)")
    parser.add_argument("--output", type=str, default="output", help="Directory to store extracted chapters")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = parse_chapter_file(args.chapters)
    splitter = M4BSplitter.from_manifest(args.input, manifest, output_dir=args.output)
    outputs = splitter.split()
    for out in outputs:
        print(out)


if __name__ == "__main__":
    main()
