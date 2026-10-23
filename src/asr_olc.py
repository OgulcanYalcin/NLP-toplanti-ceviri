"""Konuşma tanıma modellerini aynı test seti üzerinde karşılaştırır: WER, CER ve RTF.

Test seti: her ses dosyasının yanında aynı adlı .txt referans metni olan bir klasör
(MediaSpeech bu biçimde gelir; kendi kayıtlarımız da böyle konabilir).

Örnek:
    python src/asr_olc.py data/mediaspeech_tr --modeller small large-v3-turbo --sinir 200
"""

import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from faster_whisper import decode_audio

import ayarlar
from konusma import KonusmaTanima
from olcum import normalize_et, puanla

SES_UZANTILARI = {".flac", ".wav", ".ogg", ".mp3", ".m4a"}


def test_setini_oku(klasor, sinir=None):
    """Klasördeki (ses yolu, referans metin) çiftlerini ada göre sıralı döndürür."""
    ciftler = []
    for ses in sorted(Path(klasor).rglob("*")):
        referans = ses.with_suffix(".txt")
        if ses.suffix.lower() in SES_UZANTILARI and referans.exists():
            ciftler.append((ses, referans.read_text(encoding="utf-8").strip()))
    if not ciftler:
        raise SystemExit(f"{klasor} içinde .txt referansı olan ses dosyası bulunamadı.")
    return ciftler[:sinir] if sinir else ciftler


def modeli_olc(model_adi, ciftler, dil, vad=True):
    """Bir modeli bütün test setinde çalıştırır; her dosya için sonuç satırlarını döndürür."""
    konusma = KonusmaTanima(model_adi, ayarlar.CIHAZ, vad)
    etiket = model_adi if vad else f"{model_adi} (VAD yok)"
    konusma.yaziya_dok(np.zeros(ayarlar.ORNEKLEME_HIZI, dtype=np.float32), dil)  # ısınma: CUDA ilk çağrıda yavaş

    satirlar = []
    for i, (ses_yolu, referans) in enumerate(ciftler, 1):
        ses = decode_audio(str(ses_yolu), sampling_rate=ayarlar.ORNEKLEME_HIZI)
        baslangic = time.perf_counter()
        tahmin = konusma.yaziya_dok(ses, dil)
        sure = time.perf_counter() - baslangic

        ref_n, tah_n = normalize_et(referans), normalize_et(tahmin)
        wer, cer = puanla([ref_n], [tah_n]) if ref_n else (None, None)
        satirlar.append({
            "model": etiket,
            "dosya": ses_yolu.name,
            "ses_sn": round(len(ses) / ayarlar.ORNEKLEME_HIZI, 2),
            "islem_sn": round(sure, 3),
            "wer": wer,
            "cer": cer,
            "referans": ref_n,
            "tahmin": tah_n,
        })
        if i % 25 == 0:
            print(f"  {etiket}: {i}/{len(ciftler)}")
    return satirlar


def ozetle(satirlar):
    """Bir modelin satırlarından toplam WER, CER ve RTF hesaplar."""
    wer, cer = puanla([s["referans"] for s in satirlar], [s["tahmin"] for s in satirlar])
    rtf = sum(s["islem_sn"] for s in satirlar) / sum(s["ses_sn"] for s in satirlar)
    return {"wer": wer, "cer": cer, "rtf": rtf, "dosya": len(satirlar), "ses_dk": sum(s["ses_sn"] for s in satirlar) / 60}


def rapor_yaz(klasor, veri_adi, ozetler, satirlar, en_kotu):
    """Özet tabloyu ve en kötü örnekleri Markdown, tüm satırları CSV olarak yazar."""
    klasor.mkdir(parents=True, exist_ok=True)
    damga = datetime.now().strftime("%Y%m%d-%H%M")

    with open(klasor / f"asr_olcum_{damga}.csv", "w", newline="", encoding="utf-8") as f:
        yazici = csv.DictWriter(f, fieldnames=list(satirlar[0]))
        yazici.writeheader()
        yazici.writerows(satirlar)

    satir = [f"# ASR ölçümü · {veri_adi} · {damga}", "",
             "| Model | WER | CER | RTF | Dosya | Ses (dk) |", "|---|---|---|---|---|---|"]
    for model, o in ozetler.items():
        satir.append(f"| {model} | {o['wer']:.1%} | {o['cer']:.1%} | {o['rtf']:.3f} | {o['dosya']} | {o['ses_dk']:.1f} |")
    satir += ["", "RTF: işlem süresi / ses süresi (1'in altı gerçek zamandan hızlı).", ""]
    for model, kotuler in en_kotu.items():
        satir += [f"## En çok hata yapılan {len(kotuler)} dosya · {model}", ""]
        for s in kotuler:
            satir += [f"- `{s['dosya']}` WER {s['wer']:.0%}", f"  - ref: {s['referans']}", f"  - asr: {s['tahmin']}"]
        satir.append("")

    rapor = klasor / f"asr_olcum_{damga}.md"
    rapor.write_text("\n".join(satir), encoding="utf-8")
    return rapor


def main():
    ayristirici = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ayristirici.add_argument("veri", help="ses + .txt referans klasörü")
    ayristirici.add_argument("--modeller", nargs="+", default=[ayarlar.WHISPER_MODELI])
    ayristirici.add_argument("--dil", default="tr")
    ayristirici.add_argument("--sinir", type=int, help="en fazla bu kadar dosya kullan")
    ayristirici.add_argument("--cikti", default="outputs", type=Path)
    ayristirici.add_argument("--en-kotu", default=10, type=int, help="raporda listelenecek en kötü dosya sayısı")
    ayristirici.add_argument("--vad", nargs="+", choices=["acik", "kapali"], default=["acik"],
                             help="faster-whisper VAD filtresi; ikisi verilirse her model iki kez ölçülür")
    args = ayristirici.parse_args()

    ciftler = test_setini_oku(args.veri, args.sinir)
    print(f"{len(ciftler)} dosya, modeller: {', '.join(args.modeller)}, VAD: {', '.join(args.vad)}")

    tum_satirlar, ozetler, en_kotu = [], {}, {}
    for model_adi in args.modeller:
        for vad in args.vad:
            satirlar = modeli_olc(model_adi, ciftler, args.dil, vad == "acik")
            etiket = satirlar[0]["model"]
            ozetler[etiket] = ozetle(satirlar)
            puanli = [s for s in satirlar if s["wer"] is not None]
            en_kotu[etiket] = sorted(puanli, key=lambda s: s["wer"], reverse=True)[:args.en_kotu]
            tum_satirlar += satirlar
            o = ozetler[etiket]
            print(f"{etiket}: WER {o['wer']:.1%} · CER {o['cer']:.1%} · RTF {o['rtf']:.3f}")

    rapor = rapor_yaz(args.cikti, Path(args.veri).name, ozetler, tum_satirlar, en_kotu)
    print(f"\nRapor: {rapor}")


if __name__ == "__main__":
    main()
