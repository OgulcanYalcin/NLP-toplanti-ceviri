"""Kesiciyi mikrofon yerine bir ses dosyasıyla test eder."""

import numpy as np
import ayarlar
from konusma import KonusmaTanima
from faster_whisper import decode_audio
from kesici import KonusmaKesici

SES_DOSYASI = "data/kayit.ogg"

konusma = KonusmaTanima(ayarlar.WHISPER_MODELI, ayarlar.CIHAZ)
kesici = KonusmaKesici(ayarlar.ORNEKLEME_HIZI,ayarlar.SESSIZLIK_ESIGI, ayarlar.SESSIZLIK_SURESI,ayarlar.MAKS_PARCA_SURESI)

# Dosyayı 16 kHz mono ses verisine çevir
ses = decode_audio(SES_DOSYASI, sampling_rate=ayarlar.ORNEKLEME_HIZI)

# Sonuna 1 saniye sessizlik ekle; yoksa son cümle "bittti" sayılmaz
ses = np.concatenate([ses, np.zeros(ayarlar.ORNEKLEME_HIZI, dtype=np.float32)])

# Mikrofon gibi davran: sesi 0.1 saniyelik bloklar halinde kesiciye ver
blok_boyu = int(ayarlar.BLOK_SURESI * ayarlar.ORNEKLEME_HIZI)

for i in range(0, len(ses), blok_boyu):
    blok = ses[i:i + blok_boyu]
    parca = kesici.ekle(blok)
    if parca is not None:
        sure = len(parca) / ayarlar.ORNEKLEME_HIZI
        metin = konusma.yaziya_dok(parca, "tr")
        print(f"[{sure:4.1f} sn] {metin}")