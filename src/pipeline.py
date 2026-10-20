"""Ses dosyasını yazıya döküp çevirir. Modüllerin çalıştığını test etmek için."""

import time 
import ayarlar
from konusma import KonusmaTanima
from ceviri import Cevirmen

SES_DOSYASI = "data/kayit.ogg"
yon = ayarlar.YONLER["A"]

# --- Modelleri Yükle ---
print("Modeller yükleniyor...")
konusma = KonusmaTanima(ayarlar.WHISPER_MODELI, ayarlar.CIHAZ)
cevirmen = Cevirmen(yon["ceviri_modeli"], ayarlar.CIHAZ)

# --- Ses -> metin -> çeviri ---
print("İşleniyor...\n")
baslangic = time.time()

orijinal = konusma.yaziya_dok(SES_DOSYASI, yon["konusma_dili"])
ceviri = cevirmen.cevir(orijinal)

sure = time.time() - baslangic
print(f"Orijinal: {orijinal}")
print(f"Çeviri: {ceviri}")
print(f"\nİşlem süresi: {sure:.2f} saniye")


