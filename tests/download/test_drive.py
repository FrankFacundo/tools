from pathlib import Path

import pytest

from frank_tools.download import drive


class FakeResponse:
    def __init__(self, content: bytes, headers=None, cookies=None):
        self._content = content
        self.headers = headers or {}
        self.cookies = cookies or {}

    def iter_content(self, chunk_size):
        yield self._content


class SequentialSession:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def get(self, url, params=None, stream=False):
        self.calls.append({"url": url, "params": params, "stream": stream})
        return self._responses.pop(0)


def test_extract_file_id_url_and_raw():
    url = "https://drive.google.com/file/d/1IMiuHsiVvna_iN7vdZBMZy8DviFnrvYY/view?usp=sharing"
    assert drive.extract_file_id(url) == "1IMiuHsiVvna_iN7vdZBMZy8DviFnrvYY"
    assert drive.extract_file_id("plainid") == "plainid"

    with pytest.raises(ValueError):
        drive.extract_file_id("https://drive.google.com/file/x/invalid")


def test_download_file_from_link_invokes_download(monkeypatch, tmp_path):
    captured = {}

    def fake_download(file_id, output_dir="."):
        captured["file_id"] = file_id
        captured["output_dir"] = output_dir
        return Path(output_dir) / "dummy"

    monkeypatch.setattr(drive, "download_file_by_id", fake_download)
    result = drive.download_file_from_link("https://drive.google.com/file/d/abc123/view", output_dir=tmp_path)
    assert captured["file_id"] == "abc123"
    assert captured["output_dir"] == tmp_path
    assert result == tmp_path / "dummy"


def test_download_file_by_id_streams(monkeypatch, tmp_path):
    # make tqdm return the iterable directly for deterministic testing
    monkeypatch.setattr(drive, "tqdm", lambda iterable, **_: iterable)

    first = FakeResponse(
        content=b"",
        headers={},
        cookies={"download_warning_123": "token123"},
    )
    second = FakeResponse(
        content=b"hello",
        headers={"Content-Disposition": 'attachment; filename="demo.txt"'},
        cookies={},
    )
    session = SequentialSession([first, second])

    dest = drive.download_file_by_id("abc123", session=session, output_dir=tmp_path)
    assert dest == tmp_path / "demo.txt"
    assert dest.read_bytes() == b"hello"
    assert session.calls[0]["params"] == {"id": "abc123"}
    assert session.calls[1]["params"] == {"id": "abc123", "confirm": "token123"}
