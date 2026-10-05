import time
from transformers import MarianMTModel, MarianTokenizer

# --- Ayarlar ---
MODEL_ADI = "Helsinki-NLP/opus-mt-tr-en"

# --- Modeli yükle ---
print("Çeviri modeli yükleniyor...")
tokenizer = MarianTokenizer.from_pretrained(MODEL_ADI)
model= MarianMTModel.from_pretrained(MODEL_ADI).to("cuda")

# --- Çevirilecek cümleler ---
cumleler = [
    "Merhabalar ben Betül.",
    "Merhaba efendim nasılsınız?",
    "Toplantıda alınan kararları bir sonraki hafta tekrar değerlendireceğiz"
]

# --- Çevir ---
baslangic = time.time()

girdiler = tokenizer(cumleler, return_tensors="pt", padding=True).to("cuda")
ciktilar = model.generate(**girdiler, num_beams=4, max_new_tokens=256)
ceviriler = tokenizer.batch_decode(ciktilar, skip_special_tokens=True)

sure = time.time() - baslangic

for tr, en in zip(cumleler, ceviriler):
    print(f"TR: {tr}")
    print(f"EN: {en}\n")

print(f"Çeviri süresi: {sure:.2f} saniye")