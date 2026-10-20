import cuda_ayar
import queue
import re
import time
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from transformers import MarianMTModel, MarianTokenizer

# --- Ayarlar ---
WHISPER_MODELI = "small"
CEVIRI_MODELI = "Helsinki-NLP/opus-mt-tr-en"
ORNEKLEME_HIZI = 16000
PARCA_SURESI = 4

# --- Modelleri yükle ---
print ("Konuşma tanıma modeli yükleniyor...")
whisper = WhisperModel(WHISPER_MODELI, device="cuda", compute_type="float16")

print ("Çeviri modeli yükleniyor...")
tokenizer = MarianTokenizer.from_pretrained(CEVIRI_MODELI)
cevirmen = MarianMTModel.from_pretrained(CEVIRI_MODELI).to("cuda")

def cumlelere_bol(metin):
    """ Metni . ! ? işaretlerinden sonra cümlelere böler. """
    cumleler = re.split(r"(?<=[.!?])\s+", metin)
    return [c for c in cumleler if c]

def cevir(metin):
    """ Türkçe metni cümle cümle İngilizceye çevirir. """
    cumleler = cumlelere_bol(metin)
    girdiler = tokenizer(cumleler, return_tensors="pt", padding =True).to("cuda")
    ciktilar = cevirmen.generate(**girdiler, num_beams=4, max_length=256)
    ceviriler = tokenizer.batch_decode(ciktilar, skip_special_tokens=True)
    return " ".join(ceviriler)

# --- Mikrofon --> Kuyruk ---
ses_kuyrugu = queue.Queue()

def mikrofondan_gelen(veri, kare_sayisi, zaman, durum):
    """ Mikrofondan her yeni ses parçası geldiğinde otomatik çağırılır. """
    if durum: 
        print(durum)
    ses_kuyrugu.put(veri.copy())

# --- Ana döngü ---
parca_boyu = PARCA_SURESI * ORNEKLEME_HIZI
tampon = np.zeros(0, dtype=np.float32)

print("\nDinleniyor... Durdurmak için Ctrl + C\n")

with sd.InputStream(
    samplerate=ORNEKLEME_HIZI,
    channels=1,
    dtype="float32",
    callback=mikrofondan_gelen
):
    try:
        while True:
            # Kuyruktan gelen sesi tampon'a ekle
            blok = ses_kuyrugu.get()
            tampon = np.concatenate([tampon, blok.flatten()])

            # Yeterince ses biriktiyse işle
            if len(tampon) >= parca_boyu:
                parca = tampon[:parca_boyu]
                tampon = tampon[parca_boyu:]

                baslangic = time.time()
                segmentler, _ = whisper.transcribe(parca, language="tr", beam_size=5, vad_filter=True)
                turkce = " ".join(s.text.strip() for s in segmentler).strip()

                if turkce:
                    ingilizce = cevir(turkce)
                    gecikme = time.time() - baslangic
                    print(f"TR: {turkce}")
                    print(f"EN: {ingilizce}")

    except KeyboardInterrupt:
        print("\nDurduruldu.")