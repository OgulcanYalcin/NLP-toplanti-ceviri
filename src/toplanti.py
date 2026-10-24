"""İki yönlü canlı çeviri: A (mikrofon) ve B (hoparlör) aynı anda dinlenir."""

import queue
import threading
import time
import numpy as np
import ayarlar
from konusma import KonusmaTanima
from ceviri import Cevirmen
from kesici import KonusmaKesici
from ses_kaynagi import Mikrofon, HoparlorSesi
from altyazi_penceresi import AltyaziPenceresi
from altyazi_dosyası import AltyaziDosyasi

ZAMAN_ASIMI = 0.2

# --- Modelleri yükle ---
print("Modeller yükleniyor...")
konusma = KonusmaTanima(ayarlar.WHISPER_MODELI,ayarlar.CIHAZ)
cevirmenler = {ad: Cevirmen(yon["ceviri_modeli"], ayarlar.CIHAZ) for ad, yon in ayarlar.YONLER.items()}

print("Modeller ısınıyor...")
for ad, yon in ayarlar.YONLER.items():
    konusma.yaziya_dok(np.zeros(ayarlar.ORNEKLEME_HIZI,dtype=np.float32), yon["konusma_dili"])
    cevirmenler[ad].cevir("Test.")

# --- Ses kaynakları: A = mikrofon, B = hoparlör ---
kaynaklar = {
    "A": Mikrofon(ayarlar.ORNEKLEME_HIZI, ayarlar.BLOK_SURESI),
    "B": HoparlorSesi(ayarlar.ORNEKLEME_HIZI,ayarlar.BLOK_SURESI),
}

# --- Karşı tarafa altyazı (OBS bu dosyayı okur) ---
karsi_altyazi = AltyaziDosyasi(ayarlar.KARSI_ALTYAZI_DOSYASI)
is_kuyrugu = queue.Queue()
calisiyor = threading.Event()
calisiyor.set()

def dinleyici(etiket, kaynak):
    """ÜRETİCİ: Bir ses kaynağını dinler, tamamlanan konuşma parçalarını iş kuyruğuna atar."""
    kesici = KonusmaKesici(ayarlar.ORNEKLEME_HIZI, ayarlar.SESSIZLIK_ESIGI, ayarlar.SESSIZLIK_SURESI, ayarlar.MAKS_PARCA_SURESI)
    while calisiyor.is_set():
        blok = kaynak.blok_al(ZAMAN_ASIMI)
        parca = kesici.ekle(blok)
        if parca is not None:
            is_kuyrugu.put((etiket, parca, time.time()))


def isci():
    """TÜKETİCİ: İş kuyruğundan parçaları sıraylar alır, yazıya döküp çevirir."""
    while calisiyor.is_set():
        karsi_altyazi.kontrol_et()

        try:
            etiket, parca, hazir_zamani = is_kuyrugu.get(timeout=ZAMAN_ASIMI)
        except queue.Empty:
            continue

        yon = ayarlar.YONLER[etiket]
        orijinal = konusma.yaziya_dok(parca,yon["konusma_dili"])
        if not orijinal:
            continue
        ceviri = cevirmenler[etiket].cevir(orijinal)
        gecikme = time.time() - hazir_zamani

        print(f"[{etiket} | {yon['konusma_dili']}] ({gecikme:.2f} sn)")
        print(f"    Orijinal: {orijinal}")
        print(f"    Çeviri: {ceviri}\n")
        # B'nin sözlerinin çevirisi A'nın ekranındaki pencerede gösterilir
        if etiket == "B":
            pencere.goster(ceviri)

        if etiket == "A":
            karsi_altyazi.goster(ceviri)

# --- Kapanış ---
def kapat():
    """Altyazı penceresi kapanırken çağırılır: thread'leri ve ses kaynaklarını durdurur."""
    print("\nDurduruluyor...")
    calisiyor.clear()
    for t in threadler:
        t.join(timeout=2)
    for kaynak in kaynaklar.values():
        kaynak.durdur()
    karsi_altyazi.temizle()
    print("Durduruldu.")

# --- Başlat ---
pencere = AltyaziPenceresi(kapaninca=kapat)

for etiket, kaynak in kaynaklar.items():
    print(f"{etiket}: {kaynak.ad}")
    kaynak.baslat()

threadler = [threading.Thread(target=dinleyici, args=(etiket, kaynak), daemon=True) for etiket,kaynak in kaynaklar.items()]
threadler.append(threading.Thread(target=isci,daemon=True))
for t in threadler:
    t.start()

print("\nToplantı dinleniyor... Kapatmak için altyazı penceresine SAĞ TIKLA\n")
pencere.calistir()