"""Mikrofonu canlı dinler, konuşmacı duraklayınca yazıya döküp çevirir."""

import sys
import numpy as np
import queue
import time
import sounddevice as sd
import ayarlar
from konusma import KonusmaTanima
from ceviri import Cevirmen
from kesici import KonusmaKesici

# Yön komut satırından seçlilir: "python src/canli.py B". Verilmeze A kullanılır.
yon_adi = sys.argv[1] if len(sys.argv) > 1 else "A"
yon = ayarlar.YONLER[yon_adi]
print(f"Yön: {yon_adi} | Konuşma dili: {yon['konusma_dili']} | Çeviri: {yon['konusma_dili']}")

# --- Modülleri Hazırla ---
print("Modeller Yükleniyor...")
konusma = KonusmaTanima(ayarlar.WHISPER_MODELI,ayarlar.CIHAZ)
cevirmen = Cevirmen(yon["ceviri_modeli"], ayarlar.CIHAZ)
kesici = KonusmaKesici(ayarlar.ORNEKLEME_HIZI, ayarlar.SESSIZLIK_ESIGI, ayarlar.SESSIZLIK_SURESI, ayarlar.MAKS_PARCA_SURESI)

# --- Isınma: ilk gerçek konuşmanın gecikmemesi için modelleri bir kez boşta çalıştır ---
print("Modeller ısınıyor...")
konusma.yaziya_dok(np.zeros(ayarlar.ORNEKLEME_HIZI, dtype=np.float32), yon["konusma_dili"])
cevirmen.cevir("Merhaba.")

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