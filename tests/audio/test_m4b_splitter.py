from pathlib import Path

from frank_tools.audio.m4b_splitter import Chapter, M4BSplitter


def test_chapter_duration_and_str():
    chapter = Chapter(title="Intro", start=0.0, end=5.5, num=1)
    assert chapter.duration() == 5.5
    as_str = str(chapter)
    assert "Intro" in as_str and "0:00:05.500000" in as_str


def test_chapter_from_milliseconds_classmethod():
    chapter = Chapter.from_milliseconds("Intro", 0, 1500, num=1)
    assert chapter.start == 0.0
    assert chapter.end == 1.5
    assert chapter.num == 1


def test_build_ffmpeg_command():
    cmd = M4BSplitter.build_ffmpeg_command(Path("in.m4b"), Path("out.m4a"), 0.0, 10.0)
    assert cmd[:3] == ["ffmpeg", "-y", "-i"]
    assert "out.m4a" in cmd[-1]


def test_split_invokes_run_command(monkeypatch, tmp_path):
    chapters = [Chapter("One", 0.0, 1.0, num=1), Chapter("Two", 1.0, 2.0, num=2)]
    splitter = M4BSplitter("input.m4b", chapters, output_dir=tmp_path)
    called = []

    def fake_run(cmd):
        called.append(cmd)

    monkeypatch.setattr(splitter, "_run_command", fake_run)
    outputs = splitter.split()

    assert len(outputs) == 2
    assert outputs[0].name.startswith("01_")
    assert called and len(called) == 2
