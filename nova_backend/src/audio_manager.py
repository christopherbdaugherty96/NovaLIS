# ===============================================================
# NOVA INTERRUPTIBLE TTS ENGINE
# - Uses Piper TTS if available
# - Falls back to "print only" if audio libs or model missing
# ===============================================================

import asyncio
from .speech_state import speech_state  # ✅ shared, authoritative speech state

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
        self.queue = []
        self.is_playing = False
        self.stop_signal = False

        self.voice = None
        if PiperVoice is not None:
            try:
                print("🔊 Trying to load Piper voice model (en_US-lessac-medium.onnx)…")
                self.voice = PiperVoice.load("en_US-lessac-medium.onnx")
                print("✅ Piper voice loaded.")
            except Exception as e:
                print("⚠️ Could not load Piper voice model:", e)
                self.voice = None
        else:
            print("⚠️ Piper library not available; TTS will be text-only.")

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.create_task(self._worker())

    # ----------------------------------------------------------
    # BACKGROUND WORKER
    # ----------------------------------------------------------
    async def _worker(self):
        while True:
            if not self.queue or self.is_playing:
                await asyncio.sleep(0.05)
                continue

            text = self.queue.pop(0)
            await self._play_text(text)

    # ----------------------------------------------------------
    # STOP CURRENT AUDIO
    # ----------------------------------------------------------
    def stop(self):
        print("⛔ Stopping current TTS playback.")
        self.stop_signal = True
        if sd is not None:
            sd.stop()

    # ----------------------------------------------------------
    # PLAY TEXT (AUTHORITATIVE SPEECH BOUNDARY)
    # ----------------------------------------------------------
    async def _play_text(self, text: str):
        # 🔒 PHASE-2: DEFINE "WHAT WAS SPOKEN"
        speech_state.last_spoken_text = text

        print(f"[Nova speaking] {text}")
        self.is_playing = True
        self.stop_signal = False

        # If no audio stack or no Piper voice → just simulate
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

    # ----------------------------------------------------------
    # PUBLIC: QUEUE TEXT TO SPEAK
    # ----------------------------------------------------------
    def enqueue(self, text: str):
        self.queue.append(text)

# ============================================================
# SINGLETON AUDIO MANAGER (AUTHORITATIVE)
# ============================================================

audio_manager = AudioManager()


# ----------------------------------------------------------
# PHASE-2 ADAPTER (LEGACY-COMPATIBLE, SAFE)
# ----------------------------------------------------------

def nova_speak(text: str):
    """
    Phase-2 safe speech adapter.
    - Mirrors text output only
    - Non-authoritative
    - Queue-based
    - Interruptible
    """
    audio_manager.enqueue(text)
