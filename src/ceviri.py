"""Çeviri modülü:metin -> (MarianMT)."""

import re
from transformers import MarianMTModel, MarianTokenizer

def cumlelere_bol(metin):
    """"Metni . ! ? işaretlerinden sonra cümlelere böler."""
    cumleler = re.split(r"(?<=[.!?])\s+", metin)
    return [c for c in cumleler if c]

class Cevirmen:
    """"Bir dilden diğerine çeviri yapan MarianMt modeli."""

    def __init__(self, model_adi, cihaz="cuda"):
        self.cihaz=cihaz
        self.tokenizer=MarianTokenizer.from_pretrained(model_adi)
        self.model=MarianMTModel.from_pretrained(model_adi).to(cihaz)

    def cevir(self, metin):
        """"Metni cümle cümle çevirir."""
        cumleler = cumlelere_bol(metin)
        if not cumleler:
            return ""

        girdiler = self.tokenizer(cumleler, return_tensors="pt", padding=True).to(self.cihaz)
        ciktilar = self.model.generate(**girdiler, num_beams=4, max_length=256)
        ceviriler = self.tokenizer.batch_decode(ciktilar, skip_special_tokens=True)
        return " ".join(ceviriler)
    