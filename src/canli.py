"""Mikrofonu canlı dinler, konuşmacı duraklayınca yazıya döküp çevirir."""

import queue
import time
import sounddevice as sd
import ayarlar
from konusma import KonusmaTanima
from ceviri import Cevirmen
from kesici import KonusmaKesici

yon = ayarlar.YONLER["A"]

# --- Modülleri Hazırla ---
print("Modeller Yükleniyor...")
konusma = KonusmaTanima(ayarlar.WHISPER_MODELI,ayarlar.CIHAZ)
cevirmen = Cevirmen(yon["ceviri_modeli"], ayarlar.CIHAZ)
kesici = KonusmaKesici(ayarlar.ORNEKLEME_HIZI, ayarlar.SESSIZLIK_ESIGI, ayarlar.SESSIZLIK_SURESI, ayarlar.MAKS_PARCA_SURESI)

# --- Mikrofon -> kuyruk ---
ses_kuyrugu = queue.Queue()

def mikrofondan_gelen(veri, kare_sayisi, zaman, durum):
    """Mikrofondan her yeni ses bloğu geldiğinde otomatik çağırılır."""
    if durum:
        print(durum)
    ses_kuyrugu.put(veri.copy())

def isle(parca):
    """Bir konuşma parçasını yazıya döküp çevirir ve ekrana yazar."""
    baslangic = time.time()
    orijinal = konusma.yaziya_dok(parca, yon["konusma_dili"])
    if not orijinal:
        return

    ceviri = cevirmen.cevir(orijinal)
    gecikme = time.time() - baslangic
    ses_suresi = len(parca) / ayarlar.ORNEKLEME_HIZI

    print(f"[{ses_suresi:4.1f} sn konuşma | {gecikme:.2f} sn işlemi]")
    print(f" Orijinal: {orijinal}")
    print(f" Çeviri: {ceviri}\n")

# --- Ana döngü ---
blok_boyu = int(ayarlar.BLOK_SURESI * ayarlar.ORNEKLEME_HIZI)
print("\nDinleniyor... Durdurmak için Ctrl + C\n")

with sd.InputStream(samplerate=ayarlar.ORNEKLEME_HIZI, channels=1, dtype="float32", blocksize=blok_boyu, callback=mikrofondan_gelen):
    try:
        while True:
            blok = ses_kuyrugu.get().flatten()
            parca = kesici.ekle(blok)
            if parca is not None:
                isle(parca)
    except KeyboardInterrupt:
        print("\nDurduruldu.")