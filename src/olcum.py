"""Konuşma tanıma ölçümü: Türkçe metin normalizasyonu ve WER/CER hesabı."""

import re
import unicodedata

import jiwer

# Şapkalı harfler yazımdan yazıma değişir (kâğıt / kağıt); hata sayılmasın
SAPKASIZ = str.maketrans({"â": "a", "î": "i", "û": "u"})

BIRLER = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
ONLAR = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]
BUYUKLER = [(10**9, "milyar"), (10**6, "milyon"), (10**3, "bin")]


def _yuze_kadar(n):
    """0-999 arası sayıyı kelime listesine çevirir ("yüz", "bir yüz" değil)."""
    yuzler, kalan = divmod(n, 100)
    kelimeler = ([] if yuzler == 1 else [BIRLER[yuzler]]) + ["yüz"] if yuzler else []
    return kelimeler + [k for k in (ONLAR[kalan // 10], BIRLER[kalan % 10]) if k]


def sayiyi_yaz(n):
    """Tam sayıyı Türkçe okunuşuna çevirir: 344000 -> "üç yüz kırk dört bin"."""
    if n == 0:
        return "sıfır"
    kelimeler = []
    for deger, ad in BUYUKLER:
        kac, n = divmod(n, deger)
        if kac:
            kelimeler += ([] if (kac == 1 and ad == "bin") else _yuze_kadar(kac)) + [ad]
    return " ".join(kelimeler + _yuze_kadar(n))


def normalize_et(metin):
    """Metni puanlamaya hazırlar: Türkçe küçük harf, sayılar yazıyla, noktalama ve kesme işaretleri yok, tek boşluk.

    Python'un lower() fonksiyonu Türkçeyi bilmez ("I" -> "i", "İ" -> "i̇"), bu yüzden I/İ önce elle çevrilir.
    Referanslar sayıları yazıyla yazar ("kırk"), Whisper rakamla ("40"); ikisi de yazıya çevrilir.
    Sayıya bitişik ek korunur: "2si" -> "ikisi", "%50" -> "yüzde elli".
    """
    metin = unicodedata.normalize("NFC", metin)
    metin = metin.replace("I", "ı").replace("İ", "i").lower().translate(SAPKASIZ)
    metin = re.sub(r"['’`]", "", metin)                       # Ankara'ya -> ankaraya, 1'in -> 1in
    metin = re.sub(r"%\s*(?=\d)", "yüzde ", metin)
    metin = re.sub(r"(?<=\d)\.(?=\d{3}(?!\d))", "", metin)   # 344.000 -> 344000 (binlik ayracı)
    metin = re.sub(r"\d+", lambda m: " " + sayiyi_yaz(int(m.group())), metin)
    metin = re.sub(r"[^\w\s]|_", " ", metin)                   # diğer noktalama -> boşluk
    return " ".join(metin.split())


def puanla(referanslar, tahminler):
    """Bütün cümleler üzerinden toplam WER ve CER'i (0-1 arası) döndürür. Girdiler normalize edilmiş olmalı."""
    ciftler = [(r, t) for r, t in zip(referanslar, tahminler) if r]
    if not ciftler:
        raise ValueError("Puanlanacak referans yok.")
    referanslar, tahminler = zip(*ciftler)
    return jiwer.wer(list(referanslar), list(tahminler)), jiwer.cer(list(referanslar), list(tahminler))
