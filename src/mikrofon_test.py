import cuda_ayar
import time
import sounddevice as sd
from faster_whisper import WhisperModel

# --- Ayarlar ---
ORNEKLEME_HIZI = 16000 # Whisper'ın beklediği değer: saniyede 16.000 ölçüm
KAYIT_SURESI = 5 # saniye

# --- Mikrofonları listele ---
print("Bilgisayardaki ses aygıtları:")
print(sd.query_devices())
print()

# --- Modeli yükle ---
print("Model yükleniyor...")
model = WhisperModel("small", device="cuda", compute_type="float16")

# --- Kaydet ---
print(f"Kayıt birazdan başlayacak. {KAYIT_SURESI} saniye boyunca Türkçe konuş.")
for sayi in [3, 2, 1]:
    print(f"{sayi}...")
    time.sleep(1)

ses = sd.rec(
    int(KAYIT_SURESI * ORNEKLEME_HIZI),
    samplerate=ORNEKLEME_HIZI,
    channels=1,
    dtype="float32",
)
sd.wait()
print("Kayıt bitti.\n")

# --- Yazıya dök ---
ses = ses.flatten()
segmentler, _ = model.transcribe(ses, language="tr", beam_size=5)

for segment in segmentler:
    print(f"TR: {segment.text.strip()}")