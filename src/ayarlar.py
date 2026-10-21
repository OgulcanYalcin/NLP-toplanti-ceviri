"""Projenin bütün ayarları. Model veya dil değiştirmek için sadece bu dosyayı düzenle."""

# --- Donanım ---
CIHAZ ="cuda"

# --- Konuşma tanıma ---
WHISPER_MODELI = "small"

# --- Ses ---
ORNEKLEME_HIZI = 16000

BLOK_SURESI = 0.1

# --- Sessizliğe göre kesme ---
SESSIZLIK_ESIGI = 0.004

SESSIZLIK_SURESI = 0.5

MAKS_PARCA_SURESI = 10

# --- Konuşma yönleri ---
YONLER = {
    "A": {
        "konusma_dili": "tr",
        "ceviri_modeli": "Helsinki-NLP/opus-mt-tr-en",
    },
}