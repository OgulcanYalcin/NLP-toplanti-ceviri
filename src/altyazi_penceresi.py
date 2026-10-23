"""Altyazı penceresi: ekranın altında, her zaman üstte duran yarı saydam şerit."""

import queue
import time
import tkinter as tk

class AltyaziPenceresi:
    """Altyazıları gösteren çerçevesiz pencere. Sağ tıklayınca kapanır."""

    def __init__(self, kapaninca = None, satir_sayisi=2, temizleme_suresi=8):
        self.kapaninca = kapaninca
        self.satir_sayisi = satir_sayisi
        self.temizleme_suresi = temizleme_suresi
        self.kuyruk = queue.Queue()
        self.satirlar = []
        self.son_guncelleme = time.time()

        # --- Pencerenin görünümü ---
        self.pencere = tk.Tk()
        self.pencere.overrideredirect(True)
        # çerçevesiz, başlık çubuğu yok
        self.pencere.attributes("-topmost", True)
        #her zaman üstte
        self.pencere.attributes("-alpha", 0.85)
        # %85 opak(yarı saydam)
        self.pencere.configure(bg="black")

        # --- Konum: ekranın alt ortası, ekran genişiliğinin %70'i ---
        ekran_gen = self.pencere.winfo_screenwidth()
        ekran_yuk = self.pencere.winfo_screenheight()
        gen = int(ekran_gen * 0.7)
        yuk = 150
        x = (ekran_gen - gen) // 2
        y = ekran_yuk - yuk -80
        self.pencere.geometry(f"{gen}x{yuk}+{x}+{y}")

        # --- Yazı alanı ---
        self.etiket = tk.Label(self.pencere, text="Altyazı beklenyior...", fg="gray", bg="black", font=("Segoe UI", 18), wraplength= gen - 40, justify="center")
        self.etiket.pack(expand=True, fill="both",padx=20,pady=10)

        # --- Fare olayları: sol tık ile sürükle sağ tık ile kapat ---
        for parca in (self.pencere, self.etiket):
            parca.bind("<ButtonPress-1>", self._surukle_basla)
            parca.bind("<B1-Motion>", self._surukle)
            parca.bind("<Button-3>", lambda olay: self.kapat())

        # --- Kuyruk kontrolünü başlat ---
        self.pencere.after(100, self._kuyrugu_kontrol)


    def goster(self, metin):
        """Yeni bir altyazı ekler. Herhangi bir thread'den güvenle çağırılabilir."""
        self.kuyruk.put(metin)

    def _kuyrugu_kontrol(self):
        """Ana thread'de her 0.1 saniyede bir çalışır: yeni altyazı varsa gösterir."""
        yeni_var = False
        while not self.kuyruk.empty():
            self.satirlar.append(self.kuyruk.get())
            yeni_var = True

        if yeni_var:
            self.satirlar = self.satirlar[- self.satir_sayisi:]
            self.etiket.config(text="\n".join(self.satirlar),fg="white")
            self.son_guncelleme = time.time()

        elif self.satirlar and time.time() - self.son_guncelleme > self.temizleme_suresi:
            self.satirlar =[]
            self.etiket.config(text="")

        self.pencere.after(100, self._kuyrugu_kontrol)

    def _surukle_basla(self, olay):
        self._fare_x = olay.x
        self._fare_y = olay.y

    def _surukle(self, olay):
        x = self.pencere.winfo_x() + olay.x - self._fare_x
        y = self.pencere.winfo_y() + olay.y - self._fare_y
        self.pencere.geometry(f"+{x}+{y}")

    def calistir(self):
        """Pencereyi açar. Pencere kapanana kadar bu satırda beklenir. Mutlaka ana thread'de çağırılmalı."""
        self.pencere.mainloop()

    def kapat(self):
        """Pencereyi kapatır; önce varsa kapanış fonksiyonunu çağırır."""
        if self.kapaninca:
            self.kapaninca()
        self.pencere.destroy()