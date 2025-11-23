import re

from frank_tools.translate.google_free import GoogleTranslate


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_build_request_url_includes_params():
    url = GoogleTranslate.build_request_url("hola", sl="es", tl="en", hl="en", no_autocorrect=True)
    assert url.startswith("https://translate.googleapis.com")
    assert re.search(r"sl=es", url)
    assert re.search(r"tl=en", url)
    assert re.search(r"dt=qc", url)


def test_translate_parses_response(monkeypatch):
    payload = [
        [["Bonjour", "Hello", None, None]],
        None,
        "en",
        None,
        None,
        [["hello", None, [["hey"]]]],
    ]
    translator = GoogleTranslate()
    monkeypatch.setattr(translator.session, "get", lambda url, timeout: FakeResponse(payload))

    result = translator.translate("Hello", sl="en", tl="fr")
    assert result["translation"] == "Bonjour"
    assert result["original"] == "Hello"
    assert result["src_lang"] == "en"
    assert result["alternatives"] == ["hey"]
