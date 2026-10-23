"""Ses kaynakları: mikrofon ve hoparlör. İkisi de aynı şekilde kullanılır: blok_al() her zaman 16 kHz mono ses bloğu döndürür."""

import queue
import numpy as np
import sounddevice as sd
import pyaudiowpatch as pyaudio
from scipy.signal import resample_poly

class Mikrofon:
    """Varsayılan mikrofonu dinler."""

    def __init__ (self, ornekleme_hizi,blok_suresi):
        self.ornekleme_hizi = ornekleme_hizi
        self.kuyruk = queue.Queue()
        self.akis = sd.InputStream(samplerate=ornekleme_hizi, channels=1, dtype="float32", blocksize=int(ornekleme_hizi * blok_suresi), callback=self._geldi)
        self.ad = "Mikrofon"

    def _geldi(self, veri, kare_sayisi, zaman, durum):
        self.kuyruk.put(veri[:, 0].copy())

    def baslat(self):
        self.akis.start()

    def blok_al(self, zaman_asimi):
        """Bir sonraki ses bloğunu verir. Ses gelmezse aynı uzunlukta sessizlik verir."""
        try:
            return self.kuyruk.get(timeout=zaman_asimi)
        except queue.Empty:
            return np.zeros(int(self.ornekleme_hizi * zaman_asimi), dtype=np.float32)

    def durdur(self):
        self.akis.stop()
        self.akis.close()

class HoparlorSesi :
    """Varsayılan ses çıkışına (kulaklık/hoparlör) giden sesi dinler(WASAPI loopback)."""

    def __init__(self, ornekleme_hizi, blok_suresi):
        self.ornekleme_hizi = ornekleme_hizi
        self.kuyruk = queue.Queue()
        self.p = pyaudio.PyAudio()

        # Varsayılan çıkışın loopback karşılığını bul
        wasapi = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
        cikis = self.p.get_device_info_by_index(wasapi["defaultOutputDevice"])
        loopback = None
        for aygit in self.p.get_loopback_device_info_generator():
            if cikis["name"] in aygit["name"]:
                loopback = aygit
                break

        if loopback is None:
            raise RuntimeError(f"Loopback aygıtı bulunamadı: {cikis['name']}")

        self.kanal = loopback["maxInputChannels"]
        self.aygit_hizi = int(loopback["defaultSampleRate"])
        self.ad = loopback["name"]
        self.akis = self.p.open(format=pyaudio.paFloat32, channels= self.kanal, rate=self.aygit_hizi,input = True, input_device_index=loopback["index"], frames_per_buffer=int(self.aygit_hizi * blok_suresi), stream_callback= self._geldi, start= False)

    def _geldi(self, veri, kare_sayisi, zaman, durum):
        self.kuyruk.put(veri)
        return (None, pyaudio.paContinue)

    def baslat(self):
        self.akis.start_stream()

    def blok_al(self, zaman_asimi):
        """Bir sonraki ses bloğunu 16 kHz mono olarak verir. Ses gelmezse sessizlik verir."""
        try:
           ham = self.kuyruk.get(timeout=zaman_asimi)
        except queue.Empty:
            # Windows hiç ses çalmıyorken veri göndermez: biz sessizlik üretelim
            return np.zeros(int(self.ornekleme_hizi * zaman_asimi), dtype=np.float32)

        ses = np.frombuffer(ham, dtype=np.float32).reshape(-1, self.kanal).mean(axis=1)
        ses = resample_poly(ses, self.ornekleme_hizi, self.aygit_hizi)
        return ses.astype(np.float32)

    def durdur(self):
        self.akis.stop_stream()
        self.akis.close()
        self.p.terminate()

        