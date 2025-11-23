import importlib
from pathlib import Path

cli_main = importlib.import_module("frank_tools.cli.main")


def test_drive_download_dispatch(monkeypatch, capsys, tmp_path):
    captured = {}

    def fake_download(link, output_dir="."):
        captured["link"] = link
        captured["output_dir"] = output_dir
        return tmp_path / "file.bin"

    monkeypatch.setattr(cli_main, "download_file_from_link", fake_download)
    cli_main.main(["drive-download", "--link", "abc123", "--output", str(tmp_path)])

    out = capsys.readouterr().out
    assert "file.bin" in out
    assert captured["link"] == "abc123"
    assert Path(captured["output_dir"]) == tmp_path


def test_translate_dispatch(monkeypatch, capsys):
    class FakeTranslator:
        def translate(self, text, sl="auto", tl="en"):
            return {"translation": f"{text}-{tl}", "src_lang": sl}

    monkeypatch.setattr(cli_main, "GoogleTranslate", FakeTranslator)
    cli_main.main(["translate", "--text", "hola", "--tl", "en"])
    out = capsys.readouterr().out
    assert "hola-en" in out


def test_m4b_split_dispatch(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(cli_main, "parse_chapter_file", lambda path: [("One", 0.0, 1.0)])

    class FakeSplitter:
        @classmethod
        def from_manifest(cls, input_path, manifest, output_dir="."):
            return cls()

        def split(self):
            return [tmp_path / "01_One.m4a"]

    monkeypatch.setattr(cli_main, "M4BSplitter", FakeSplitter)
    cli_main.main(["m4b-split", "--input", "file.m4b", "--chapters", "chapters.txt", "--output", str(tmp_path)])
    out = capsys.readouterr().out
    assert "01_One.m4a" in out
