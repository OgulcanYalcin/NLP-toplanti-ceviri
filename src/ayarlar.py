"""Projenin bütün ayarları. Model veya dil değiştirmek için sadece bu dosyayı düzenle."""

# --- Donanım ---
CIHAZ ="cuda"

# --- Konuşma tanıma ---
WHISPER_MODELI = "small"

# --- Ses ---
ORNEKLEME_HIZI = 16000

# --- Konuşma yönleri ---
YONLER = {
    "A": {
        "konusma_dili": "tr",
        "ceviri_modeli": "Helsinki-NLP/opus-mt-tr-en",
    },
}