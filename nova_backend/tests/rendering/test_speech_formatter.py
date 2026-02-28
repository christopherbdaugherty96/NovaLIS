from src.rendering.speech_formatter import SpeechFormatter


def test_speech_formatter_adds_pause_markers_between_sentences():
    fmt = SpeechFormatter()
    out = fmt.format_for_tts("First sentence. Second sentence!")
    assert " … " in out
