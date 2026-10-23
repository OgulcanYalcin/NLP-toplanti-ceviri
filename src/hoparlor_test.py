"""Hoparlöre giden sesi(WASAPI loopback) birkaç saniye kaydedip yazıya döker."""

import time
import numpy as np
import ayarlar
from konusma import KonusmaTanima
import pyaudiowpatch as pyaudio
from scipy.signal import resample_poly

KAYIT_SURESI = 5
BLOK_SURESI = 0.1

p = pyaudio.PyAudio()

# --- 1. Varsayılan ses çıkışını bul (kulaklık veya hoparlör) ---
wasapi = p.get_host_api_info_by_type(pyaudio.paWASAPI)
cikis = p.get_device_info_by_index(wasapi["defaultOutputDevice"])
print(f"Varsayılan ses çıkışı: {cikis['name']}")

# --- 2. Bu çıkışın loopback karşılığını bul ---
loopback = None
for aygit in p.get_loopback_device_info_generator():
    if cikis ["name"] in aygit["name"]:
        loopback = aygit
        break

if loopback is None:
    raise SystemExit("Loopback aygıtı bulunamadı!")

kanal = loopback["maxInputChannels"]
hiz = int(loopback["defaultSampleRate"])
print(f"Loopback aygıtı: {loopback['name']} | {kanal} kanal | {hiz} Hz\n")

# --- 3. Modeli yükle ---
print("Model yükleniyor...")
konusma = KonusmaTanima(ayarlar.WHISPER_MODELI,ayarlar.CIHAZ)

# --- 4. Kaydet ---
print("\nİngilizce bir videoyu ŞİMDİ oynat. 3 saniye sonra kayıt başlıyor...")
time.sleep(3)
print("Kayıt başladı...")

blok_boyu = int(hiz * BLOK_SURESI)
akis = p.open(format=pyaudio.paFloat32, channels=kanal, rate=hiz, input= True, input_device_index=loopback["index"], frames_per_buffer = blok_boyu)

bloklar = []
for _ in range(int(KAYIT_SURESI / BLOK_SURESI)):
    veri = akis.read(blok_boyu, exception_on_overflow=False)
    bloklar.append(np.frombuffer(veri, dtype=np.float32))

akis.stop_stream()
akis.close()
p.terminate()
print("Kayıt bitti.\n")

# --- 5. Whisper'ın istediği biçime çevir: mono, 16 khz ---
ses = np.concatenate(bloklar)
ses = ses.reshape(-1, kanal).mean(axis=1)
# stereo -> mono
ses = resample_poly(ses, ayarlar.ORNEKLEME_HIZI, hiz)
ses = ses.astype(np.float32)

seviye = np.sqrt(np.mean(ses ** 2))
print(f"Ses seviyesi (RMS): {seviye:.4f}")

# --- 6. Yazıya dök ---
metin = konusma.yaziya_dok(ses, "en")
print(f"Duyulan: {metin}")
