"""Sessizliğe göre kesme modülü: ses bloklarını konuşma parçalarına ayırır."""

import numpy as np

class KonusmaKesici:
    """Gelen ses bloklarını biriktirir; konuşmacı duraklayınca tamamlanmış parçayı verir."""

    def __init__(self, ornekleme_hizi, esik,sessizlik_suresi, maks_sure):
        self.ornekleme_hizi = ornekleme_hizi
        self.esik = esik
        self.sessizlik_suresi = sessizlik_suresi
        self.maks_sure = maks_sure
        self._sifirla()

    def _sifirla(self):
        """Yeni bir konuşma parçası için her şeyi başa döndürür."""
        self.tampon = np.zeros(0, dtype=np.float32)
        self.sessiz_sure = 0.0
        self.konusma_var = False

    def ekle(self, blok):
        """"Yeni bir ses bloğu ekler.Bir konuşma parçası tamamlandıysa onu döndürür, tamamlanmadıysa None döndürür."""
        self.tampon = np.concatenate([self.tampon,blok])
        blok_suresi = len(blok) / self.ornekleme_hizi
        yukseklik = np.sqrt(np.mean(blok ** 2))

        if yukseklik > self.esik:
            self.konusma_var = True
            self.sessiz_sure = 0.0
        else:
            self.sessiz_sure += blok_suresi

        tampon_suresi = len(self.tampon) / self.ornekleme_hizi

        # Konuşma bitti ya da çok uzadı: parçayı teslim et
        
        if self.konusma_var and (self.sessiz_sure >= self.sessizlik_suresi or tampon_suresi >= self.maks_sure):
            parca = self.tampon
            self._sifirla()
            return parca
        
        # Kimse konuşmuyor: son 0.5 saniye hariç eski sessizliği at
        if not self.konusma_var and tampon_suresi > 1.0:
            self.tampon = self.tampon[-int(0.5 * self.ornekleme_hizi):]

        return None