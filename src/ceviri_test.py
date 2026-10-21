"""Çeviri modülünü metinle test eder. Yön değiştirmek için YON satırını düzenle."""

import time
import ayarlar
from ceviri import Cevirmen

YON="B"

cumleler = [
    "Hello, welcomte to the meeting.",
    "Lets go over last week's sales numbers.",
    "I'll send yo the report by Friday.",
    "We need to meet the deadline.",
    "Mr. Smith will join us later.",
]

yon = ayarlar.YONLER[YON]
print(f"Model yükleniyor: {yon['ceviri_modeli']}")
cevirmen = Cevirmen(yon["ceviri_modeli"], ayarlar.CIHAZ)
cevirmen.cevir("Hello.")

for cumle in cumleler:
    baslangic = time.time()
    ceviri = cevirmen.cevir(cumle)
    sure = time.time() - baslangic
    print(f"\n{cumle}\n-> {ceviri} ({sure:.2f} sn)")