from pathlib import Path
from threading import RLock


class TranscriptionEngine:
    def __init__(self, model_size: str = "tiny", device: str = "auto", compute_type: str = "int8") -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None
        self._lock = RLock()

    def transcribe(self, audio_path: Path) -> str:
        with self._lock:
            try:
                return self._transcribe(audio_path)
            except Exception:
                if (self.device, self.compute_type) == ("cpu", "int8"):
                    raise
                self._model = None
                self.device, self.compute_type = "cpu", "int8"
                return self._transcribe(audio_path)

    def _transcribe(self, audio_path: Path) -> str:
        segments, _ = self._load_model().transcribe(str(audio_path), vad_filter=True, beam_size=5)
        return " ".join(text for segment in segments if (text := getattr(segment, "text", "").strip()))

    def _load_model(self):
        with self._lock:
            if self._model is None:
                from faster_whisper import WhisperModel

                self._model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
            return self._model
