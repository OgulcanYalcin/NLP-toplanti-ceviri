"""Çeviri modülü:metin -> (MarianMT)."""

import re
from transformers import MarianMTModel, MarianTokenizer

# Sonundaki nokta cümle sonu sayılmayacak kısaltmalar (küçük harfle)
KISALTMALAR = {"mr.", "mrs.", "ms.", "dr.", "prof.", "st.", "vs.", "etc.", "sn.", "vb."}

def cumlelere_bol(metin):
    """"Metni . ! ? işaretlerinden sonra cümlelere böler. Kısaltmalarda bölmez."""
    parcalar = re.split(r"(?<=[.!?])\s+", metin)

    cumleler = []
    for parca in parcalar:
        if not parca:
            continue

        if cumleler and cumleler[-1].split()[-1].lower() in KISALTMALAR:
            cumleler[-1] += " " + parca
        else:
            cumleler.append(parca)
    return cumleler

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
    