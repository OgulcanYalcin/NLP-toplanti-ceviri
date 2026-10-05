import cuda_ayar
import time
from faster_whisper import WhisperModel

#--- Ayarlar ---
MODEL_ADI= "small"
SES_DOSYASI = "data/kayit.ogg"

#--- Modeli yükle ---
print("Model yükleniyor...")
model = WhisperModel(MODEL_ADI, device="cuda", compute_type="float16")

#--- Yazıya dök ---
print("Ses yazıya dökülüyor...")
baslangic = time.time()

segmentler, bilgi = model.transcribe(SES_DOSYASI, language="tr", beam_size=5)

for segment in segmentler:
    print(f"[{segment.start:6.2f}s -> {segment.end:6.2f}s] {segment.text}")

sure = time.time() - baslangic
print(f"\nSes uzunluğu : {bilgi.duration:.1f} saniye")
print(f"İşlem süresi : {sure:.1f} saniye")