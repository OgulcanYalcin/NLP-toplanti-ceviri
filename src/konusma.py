"""Konuşma tanıma modülü: ses->metin (Whisper)."""

import cuda_ayar
from faster_whisper import WhisperModel
from segment import Segment

class KonusmaTanima:
    """Sesi yazıya döken whisper modeli."""

    def __init__(self, model_adi, cihaz="cuda", vad=True):
        """vad: faster-whisper'ın kendi Silero VAD filtresi (sessiz kısımları atlar; müzikli konuşmayı da atabilir)."""
        hesaplama_tipi="float16" if cihaz=="cuda" else "int8"
        self.model = WhisperModel(model_adi, device=cihaz, compute_type=hesaplama_tipi)
        self.vad = vad

    def _coz(self, ses, dil):
        """Whisper çıktısındaki boş olmayan parçaları döndürür."""
        segmentler, _ = self.model.transcribe(ses, language=dil, beam_size=5, vad_filter=self.vad)
        return [s for s in segmentler if s.text.strip()]

    def yaziya_dok(self, ses, dil):
        """Ses dosyasını veya ses verisini verilen dilde yazıya döker."""
        return " ".join(s.text.strip() for s in self._coz(ses, dil))

    def segmentlere_dok(self, ses, dil, konusmaci="ben", kayma=0.0):
        """Sesi zaman damgalı Segment listesine çevirir.

        kayma: ses parçasının toplantı başından itibaren başladığı saniye; zaman damgaları buna eklenir.
        """
        return [
            Segment(kayma + s.start, kayma + s.end, s.text.strip(), dil, konusmaci)
            for s in self._coz(ses, dil)
        ]
