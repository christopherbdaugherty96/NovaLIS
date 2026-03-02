# ===============================================================
# NOVA INVOCATION-BOUND TTS ENGINE (PHASE-4 COMPLIANT)
# - No background worker
# - No polling loops
# - No ambient execution
# - Invocation-scoped playback only
# ===============================================================

import asyncio
from .speech_state import speech_state  # authoritative speech record

try:
    import sounddevice as sd
    import soundfile as sf
except Exception:
    sd = None
    sf = None

try:
    from piper import PiperVoice
except Exception:
    PiperVoice = None


class AudioManager:
    def __init__(self):
        self.is_playing = False
        self.stop_signal = False
        self.voice = None

        if PiperVoice is not None:
            try:
                print("🔊 Loading Piper voice model (en_US-lessac-medium.onnx)…")
                self.voice = PiperVoice.load("en_US-lessac-medium.onnx")
                print("✅ Piper voice loaded.")
            except Exception as e:
                print("⚠️ Piper model load failed:", e)
                self.voice = None
        else:
            print("⚠️ Piper not available. TTS will simulate text only.")

    # ----------------------------------------------------------
    # STOP CURRENT AUDIO (INVOCATION-SCOPED)
    # ----------------------------------------------------------
    def stop(self):
        if not self.is_playing:
            return

        print("⛔ Stopping current TTS playback.")
        self.stop_signal = True

        if sd is not None:
            try:
                sd.stop()
            except Exception:
                pass

    # ----------------------------------------------------------
    # PUBLIC SPEAK ENTRY (NO QUEUE, DIRECT INVOCATION)
    # ----------------------------------------------------------
    def speak(self, text: str):
        """
        Invocation-bound speech entry.
        No background worker.
        No polling.
        Single-shot execution only.
        """
        if not text:
            return

        # Prevent overlapping speech
        if self.is_playing:
            self.stop()

        asyncio.create_task(self._play_text(text))

    # ----------------------------------------------------------
    # INTERNAL PLAYBACK ROUTINE
    # ----------------------------------------------------------
    async def _play_text(self, text: str):
        speech_state.last_spoken_text = text

        print(f"[Nova speaking] {text}")

        self.is_playing = True
        self.stop_signal = False

        # Fallback mode (no audio stack)
        if self.voice is None or sd is None or sf is None:
            await asyncio.sleep(min(3.0, max(1.0, len(text) / 20.0)))
            self.is_playing = False
            return

        try:
            wav_bytes = self.voice.synthesize(text)

            import io
            buf = io.BytesIO(wav_bytes)
            audio, sr = sf.read(buf, dtype="float32")

            chunk_size = 4096

            for i in range(0, len(audio), chunk_size):
                if self.stop_signal:
                    break

                sd.play(audio[i:i + chunk_size], sr)
                await asyncio.sleep(chunk_size / sr)

            sd.stop()

        except Exception as e:
            print("TTS playback error:", e)

        self.is_playing = False


# ============================================================
# SINGLETON INSTANCE (NO BACKGROUND TASKS)
# ============================================================

audio_manager = AudioManager()


# ----------------------------------------------------------
# PHASE-4 SAFE SPEECH ADAPTER
# ----------------------------------------------------------

def nova_speak(text: str):
    """
    Invocation-bound speech adapter.
    - No background worker
    - No queue
    - No ambient processing
    - Interruptible
    """
    audio_manager.speak(text)