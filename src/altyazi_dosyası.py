"""Karşı tarafa gösterilecek altyazıyı bir metin dosyasına yazar. OBS bu dosyayı okuyup kamera görüntüsünün üzerine yerleştirir."""

import os
import time

class AltyaziDosyasi:
    """Son altyazıları bir dosyaya yazar; bir süre yeni altyazı gelmezse dosyayı temizler."""

    def __init__(self, dosya_yolu,satir_sayisi=2,temizleme_suresi=8):
        self.dosya_yolu = dosya_yolu
        self.satir_sayisi = satir_sayisi
        self.temizleme_suresi = temizleme_suresi
        self.satirlar = []
        self.son_guncelleme = time.time()

        os.makedirs(os.path.dirname(dosya_yolu), exist_ok=True)
        self.temizle()


    def goster(self, metin):
        """Yeni bir altyazı ekler ve dosyayı günceller."""
        self.satirlar = (self.satirlar + [metin])[- self.satir_sayisi:]
        self.son_guncelleme = time.time()
        self._yaz("\n".join(self.satirlar))

    def kontrol_et(self):
        """Uzun süredir yeni altyazı gelmediyse dosyayı temizler. Düzenli olarak çağırılmalı."""
        if self.satirlar and time.time() - self.son_guncelleme > self.temizleme_suresi:
            self.temizle()

    def temizle(self):
        """Altyazıyı siler (dosyayı boşaltır)."""
        self.satirlar = []
        self._yaz("")

    def _yaz(self,metin):
        """Dosyayı güvenli şekilder yazar: önce geçici dosyaya, sonra tek hamlede yer değiştirir."""
        gecici = self.dosya_yolu + ".tmp"
        with open(gecici, "w", encoding="utf-8") as f:
            f.write(metin)
        try:
            os.replace(gecici, self.dosya_yolu)
        except :
            # OBS dosyayı tam o an okuyorsa yer değiştirme reddedilebilir: doğrudan yaz
            with open(self.dosya_yolu,"w", encoding="utf-8") as f:
                f.write(metin)
