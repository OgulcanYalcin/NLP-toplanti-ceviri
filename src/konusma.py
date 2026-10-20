"""Konuşma tanıma modülü: ses->metin (Whisper)."""

import cuda_ayar
from faster_whisper import WhisperModel

class KonusmaTanima:
    """Sesi yazıya döken whisper modeli."""

    def __init__(self,model_adi, cihaz="cuda"):
        hesaplama_tipi="float16" if cihaz=="cuda" else "int8"
        self.model = WhisperModel(model_adi, device=cihaz, compute_type=hesaplama_tipi)

    def yaziya_dok(self, ses, dil):
        """"Ses dosyasını veya ses verisini verilen dilde yazıya döker."""
        segmentler, _ = self.model.transcribe(ses, language=dil, beam_size=5, vad_filter=True)
        return " ".join(s.text.strip() for s in segmentler).strip()
    