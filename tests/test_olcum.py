"""olcum.py testleri (GPU gerekmez)."""

import pytest

from olcum import normalize_et, puanla, sayiyi_yaz


@pytest.mark.parametrize("sayi, beklenen", [
    (0, "sıfır"),
    (7, "yedi"),
    (40, "kırk"),
    (64, "altmış dört"),
    (100, "yüz"),
    (345, "üç yüz kırk beş"),
    (1000, "bin"),
    (1100, "bin yüz"),
    (2016, "iki bin on altı"),
    (344000, "üç yüz kırk dört bin"),
    (1_000_000, "bir milyon"),
    (2_500_000_000, "iki milyar beş yüz milyon"),
])
def test_sayiyi_yaz(sayi, beklenen):
    assert sayiyi_yaz(sayi) == beklenen


@pytest.mark.parametrize("girdi, beklenen", [
    ("IRMAK", "ırmak"),
    ("İSTANBUL", "istanbul"),
    ("Işık İçin", "ışık için"),
    ("Ankara'ya gittim.", "ankaraya gittim"),
    ("Ankara’ya", "ankaraya"),
    ("Merhaba, nasılsınız?!", "merhaba nasılsınız"),
    ("yarı-zamanlı   iş", "yarı zamanlı iş"),
    ("Kâğıt ve hâlâ", "kağıt ve hala"),
    ("40 versek yarın 30 da", "kırk versek yarın otuz da"),
    ("100 mezundan 2si", "yüz mezundan ikisi"),
    ("artık %50'den fazlası", "artık yüzde elliden fazlası"),
    ("50 artı 1'in", "elli artı birin"),
    ("344.000 lira", "üç yüz kırk dört bin lira"),
    ("0,64'lük", "sıfır altmış dörtlük"),
    ("  ", ""),
])
def test_normalize_et(girdi, beklenen):
    assert normalize_et(girdi) == beklenen


def test_birlesik_noktali_i_tek_harf_olur():
    # "i̇" (i + birleşik nokta), lower("İ") sonucunda oluşur; "i" ile aynı sayılmalı
    assert normalize_et("İ") == normalize_et("i")


def test_puanla_ayni_metin_sifir():
    assert puanla(["bir iki üç"], ["bir iki üç"]) == (0.0, 0.0)


def test_puanla_toplam_kelime_uzerinden():
    # 1. cümlede 1 hata / 4 kelime, 2. cümlede 0 / 1 -> toplam 1/5
    wer, _ = puanla(["bir iki üç dört", "beş"], ["bir iki üç beş", "beş"])
    assert wer == pytest.approx(0.2)


def test_puanla_bos_tahmin_tum_kelimeler_silinmis():
    wer, cer = puanla(["bir iki"], [""])
    assert wer == 1.0 and cer == 1.0


def test_puanla_bos_referanslar_atlanir():
    assert puanla(["", "bir"], ["bir şey", "bir"]) == (0.0, 0.0)


def test_puanla_referans_yoksa_hata():
    with pytest.raises(ValueError):
        puanla([""], ["bir"])
