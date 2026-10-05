import cuda_ayar
import re
import time
from faster_whisper import WhisperModel
from transformers import MarianMTModel, MarianTokenizer

# --- Ayarlar ---
WHISPER_MODELI = "small"
CEVIRI_MODELI = "Helsinki-NLP/opus-mt-tr-en"
SES_DOSYASI = "data/kayit.ogg"

# --- Modelleri yükle ---
print("Konuşma tanıma modeli yükleniyor...")
whisper = WhisperModel(WHISPER_MODELI, device="cuda", compute_type="float16")

print("Çeviri modeli yükleniyor...")
tokenizer = MarianTokenizer.from_pretrained(CEVIRI_MODELI)
cevirmen = MarianMTModel.from_pretrained(CEVIRI_MODELI).to("cuda")

def cumlelere_bol(metin):
    """Metni . ! ? işaretlerinden sonra cümlelere böler."""
    cumleler = re.split(r"(?<=[.!?])\s+", metin)
    return [c for c in cumleler if c]


def cevir(metin):
    """Türkçe metni cümle cümle İngilizceye çevirir."""
    cumleler = cumlelere_bol(metin)
    girdiler= tokenizer(cumleler, return_tensors="pt", padding=True).to("cuda")
    ciktilar = cevirmen.generate(**girdiler, num_beams=4, max_length=256)
    ceviriler = tokenizer.batch_decode(ciktilar, skip_special_tokens=True)
    return " ".join(ceviriler)

# --- Ses --> Türkçe metin --> İngilizce metin ---
print("İşleniyor...\n")
baslangic = time.time()

segmentler, bilgi = whisper.transcribe(SES_DOSYASI, language="tr", beam_size=5)

for segment in segmentler :
    turkce = segment.text.strip()
    ingilizce = cevir(turkce)

    print(f"[{segment.start:6.2f}s -> {segment.end:.2f}s]")
    print(f"   TR: {turkce}")
    print(f"   EN: {ingilizce}\n")

sure = time.time() - baslangic
print(f"Ses uzunluğu : {bilgi.duration:.1f} saniye")
print(f"İşlem süresi: {sure:.1f} saniye")