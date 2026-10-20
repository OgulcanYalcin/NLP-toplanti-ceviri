"""Mikrofonun ses seviyesini 10 saniye boyunca ekrana yazar. Eşik ayarı için."""

import time 
import numpy as np
import sounddevice as sd
import ayarlar

OLCUM_SURESI = 10

def geldi(veri, kare_sayisi, zaman, durum):
    yukseklik = float(np.sqrt(np.mean(veri**2)))
    cubuk = "#" * int(yukseklik * 500)
    print(f"{yukseklik:.4f} {cubuk}")

print(f"{OLCUM_SURESI} saniye ölçüm. Önce bir kaç saniye SUS, sonra KONUŞ\n")
with sd.InputStream(samplerate=ayarlar.ORNEKLEME_HIZI, channels=1, dtype="float32", blocksize=int(ayarlar.BLOK_SURESI * ayarlar.ORNEKLEME_HIZI), callback=geldi):time.sleep(OLCUM_SURESI)