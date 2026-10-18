# Kapsam

Durum: **taslak, ekip onayı bekliyor** (18 Eki 2026).

## Problem

Çevrimiçi toplantılarda katılımcılar aynı dili konuşmuyor. Uygulama toplantıyı dinler, her konuşmayı
hedef dile çevirir, altyazı (ve istenirse ses) olarak verir ve toplantı sonunda iki dilli transkript kaydeder.

Her dil çifti için ayrı bir **istemci** (client) çalışır: örneğin TR → EN istemcisi Türkçe konuşmaları
İngilizceye çevirir, DE → EN istemcisi Almancaları. İstemci kendi hedef dilinde bir transkript tutar.

## İlk dil çifti

**Türkçe → İngilizce.** Mevcut kod (`pipeline.py`) bu çift için çalışıyor, ekibin ana dili Türkçe
olduğu için test verisi toplamak ve sonuçları kontrol etmek kolay. Bkz. [D-001](decisions.md).

## İş bölümü

| Adım | İş | Sahibi |
|---|---|---|
| 1 | Sesi metne çevir (ASR) | Tolga |
| 2 | Metni hedef dile çevir (MT) | ekip |
| 3 | Çevrilen metni sese çevir (TTS) | ekip |

## Kapsamda (v1, demo: 21-25 Ara)

- Toplantı sesini canlı yakalama: kendi mikrofonumuz + bilgisayardan çıkan ses (Windows, WASAPI loopback).
- Türkçe konuşmayı canlı yazıya dökme (adım 1).
- Kesinleşen her cümleyi İngilizceye çevirme (adım 2).
- Çeviriyi altyazı olarak gösterme; isteğe bağlı İngilizce seslendirme (adım 3).
- Toplantı sonunda iki dilli transkript (TR + EN, zaman damgalı).
- Ölçüm: ASR için WER/CER, çeviri için BLEU/chrF, uçtan uca gecikme.
- En az bir modelde ince ayar ve hazır modelle karşılaştırma (ders gereği).

## Uç adımlar (zaman kalırsa)

- Birden fazla istemciyi aynı anda çalıştırmak (ör. TR → EN ve DE → EN birlikte).
- Diller için güvenilirlik listesi: her dil çiftinde ASR ve çeviri kalitesinin ölçülüp listelenmesi.
- Teams entegrasyonu (uygulama sesini doğrudan almak, altyazıyı toplantıya yansıtmak).

## Kapsam dışı (v1)

- Bulut API'leri (OpenAI, Google, Azure): her şey yerel modellerle, tek NVIDIA GPU'lu Windows makinede çalışır.
  Hem gizlilik (toplantı kaydı dışarı çıkmaz) hem ders hedefi (modelleri kendimiz çalıştırıp ince ayar yapmak) için.
- Gerçek konuşmacı ayrımı (diarization). v1'de yalnızca "ben" (mikrofon) / "karşı taraf" (loopback) ayrımı var.
- Mobil, web veya macOS/Linux istemcisi.

## Başarı ölçütleri (öneri, ekipçe kesinleşmeli)

- Konuşma bitişinden altyazının görünmesine kadar ortalama gecikme **3 saniyenin altında**.
- Türkçe ASR WER'i hazır `small` modele göre belirgin şekilde daha düşük (hedef değer ölçümden sonra konacak).
- 30 dakikalık bir toplantı çökmeden çalışır ve transkript dosyası kaydedilir.

## Kısıtlar

- Windows, Python 3.11, NVIDIA GPU (CUDA). Geliştirme makinelerinden biri RTX 3060 12 GB.
- Ses verileri ve toplantı kayıtları repoya girmez (`data/` ve `outputs/` `.gitignore`'da).
- Ara dönem sınavı haftası (2-6 Kas) boyunca iş durur.

## Açık sorular

- Hocanın beklediği teslim biçimi (demo, rapor, kod) ve kesin tarih.
- v1'de sadece Türkçe konuşma mı, yoksa dil otomatik algılansın mı?
- Adım 2 ve 3'ün sahipleri.
