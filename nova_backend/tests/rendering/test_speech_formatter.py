from src.rendering.speech_formatter import SpeechFormatter


def test_speech_formatter_adds_pause_markers_between_sentences():
    fmt = SpeechFormatter()
    out = fmt.format_for_tts("First sentence. Second sentence!")
    assert " … " in out


def test_speech_formatter_masks_urls_and_paths_for_tts():
    fmt = SpeechFormatter()
    out = fmt.format_for_tts("Open https://example.com from /tmp/demo.txt")
    assert "http" not in out.lower()
    assert "/tmp" not in out
