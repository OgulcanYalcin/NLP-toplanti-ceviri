# Adım 1 · Sesi metne çevirme (ASR) araştırması

Bu belge iş bölümündeki 1. adım için ("sesi metne çevir") seçenekleri ve önerilen yolu özetler.
Durum: **taslak, ekip incelemesi bekliyor** (18 Eki 2026).

## Hedef

Toplantı sesini canlı dinleyip konuşmayı düşük gecikmeyle metne dökmek ve her parçayı
2. adıma (çeviri) aktarmak. İlk dil çifti TR → EN, ileride başka diller.

## Şu anki durum (repo)

- `faster-whisper` ile `small` model, CUDA + float16, dil sabit `tr`.
- `transcribe.py` / `pipeline.py` dosyadan çalışıyor; `mikrofon_test.py` 5 saniye kaydedip yazıya döküyor.
- Henüz yok: sürekli (streaming) giriş, VAD, toplantı sesini yakalama, ölçüm (WER, gecikme).
- Not: `requirements.txt` UTF-16 kaydedilmiş ve bir satır bozuk (`filelock==3.32.3git`); ayrı bir PR'da düzeltilebilir.

Geliştirme makinesi: RTX 3060 12 GB. `large-v3-turbo` float16 ile rahat sığar; LoRA ile ince ayar da bu kartta yapılabilir.

## 1. Model seçenekleri

| Model | Türkçe | Artı | Eksi |
|---|---|---|---|
| Whisper `small` (şu an) | Var | Hızlı, küçük | Türkçede belirgin şekilde daha fazla hata |
| Whisper `large-v3-turbo` | Var | large-v3'e yakın doğruluk, çok daha hızlı (decoder budanmış, 809M), MIT | `small`'dan yavaş |
| Whisper `large-v3` | Var | En doğru Whisper | Turbo'dan belirgin şekilde yavaş (32 decoder katmanı, turbo'da 4), canlı kullanım için ağır |
| Türkçe ince ayarlı Whisper (ör. `selimc/whisper-large-v3-turbo-turkish`) | Sadece TR | Türkçeye özel | Rapor edilen WER'ler (~13-19) farklı test setlerinde, karşılaştırılamaz; doğrulanmalı |
| Qwen3-ASR 0.6B / 1.7B | Var (resmi listede) | Yeni, çok dilli | Türkçe WER yayımlanmamış; faster-whisper ekosistemi dışında |
| NVIDIA Parakeet / Canary | Belirsiz | Avrupa dillerinde çok hızlı | Türkçe desteği doğrulanamadı |

**Öneri:** varsayılanı `large-v3-turbo` yapmak; Türkçe ince ayarlı sürümleri ve Qwen3-ASR'ı aynı test setinde ölçüp karar vermek.
Yayımlanmış rakamlar farklı normalizasyon ve veri bölümleri kullandığı için tek başına güvenilir değil.

## 2. Canlı (streaming) yazıya dökme

Whisper 30 saniyelik pencerelerle çalışır, doğal olarak streaming değildir. Yaygın çözümler:

| Yaklaşım | Nasıl | Not |
|---|---|---|
| VAD + parça parça | Silero VAD konuşmayı bölür, her konuşma parçası faster-whisper'a gider | En basit; cümle sonunu beklediği için gecikme ~konuşma uzunluğu |
| LocalAgreement (`ufal/whisper_streaming`) | Büyüyen ses tamponu tekrar tekrar çözülür, ardışık iki çözümde aynı kalan kelimeler "kesinleşir" | Kelime kelime çıktı, faster-whisper backend'i önerilir |
| SimulStreaming (`ufal/SimulStreaming`) | AlignAtt politikası, whisper_streaming'in halefi | Yazarlarına göre ~5 kat daha hızlı; araştırma kodu |
| Hazır sunucu: WhisperLiveKit / WhisperLive | WebSocket ile ses gönder, metin al; ikisi de yukarıdaki politikaları içerir | Çoklu client (uç adım) için doğal mimari |

**Öneri:** önce kendi küçük döngümüzü (VAD + LocalAgreement mantığı) yazıp gecikmeyi ölçmek, sonra WhisperLiveKit ile kıyaslamak.
Çoklu client hedefine geçildiğinde sunucu yapısı (tek GPU'da bir model, birden çok bağlantı) WhisperLiveKit/WhisperLive ile hazır gelir.

## 3. Toplantı sesini yakalama (Windows)

- **Mikrofon:** `sounddevice` (zaten kullanılıyor).
- **Toplantıdaki diğer kişiler:** WASAPI loopback ile hoparlöre giden sesi yakalamak. `PyAudioWPatch` bunun için yaygın seçim (`get_default_wasapi_loopback()`).
  `soundcard` kütüphanesi de destekliyor ama Windows'ta tek kanal kayıtta bozuk ses bildirilmiş.
- Loopback tüm sistem sesini alır (sadece Teams/Zoom değil). Uygulama bazlı yakalama ayrı bir iş; Teams entegrasyonu uç adımında ele alınabilir.
- Kendi sesimiz ve karşı tarafın sesi ayrı akış olarak tutulursa "kim konuştu" bilgisi bedavaya gelir.

## 4. Veri (değerlendirme ve ince ayar)

| Veri seti | Boyut | Lisans | Kullanım |
|---|---|---|---|
| Common Voice Scripted 25.0 · TR | ~129 saat doğrulanmış, ~1.800 konuşmacı | CC0, ama yeniden paylaşım yasak | Eğitim + test |
| ISSAI Turkish Speech Corpus | ~218 saat | HF kartında MIT (GitHub'dan teyit edilmeli) | Eğitim |
| MediaSpeech · TR (OpenSLR 108) | ~10 saat, medya/YouTube | CC BY 4.0 | Test (toplantıya daha yakın, doğal konuşma) |
| Kendi toplantı kayıtlarımız | Az | Bizim (kişisel veri) | Asıl test seti |

Ses verileri repoya girmez (`data/` zaten `.gitignore`'da); Common Voice lisansı da bunu gerektiriyor.

## 5. Ölçüm

- **WER ve CER** (`jiwer`, zaten bağımlılıklarda). Türkçe normalizasyona dikkat: Python'un `lower()` fonksiyonu `I → i` yapar, Türkçede `I → ı` ve `İ → i` olmalı. Normalizasyon tek bir fonksiyonda tutulmalı, yoksa sonuçlar şişer.
- **RTF** (işlem süresi / ses süresi) ve **gecikme**: konuşma bitişinden metnin ekrana gelmesine kadar geçen süre (ortalama ve p90).
- Aynı test seti, aynı normalizasyon, tüm modeller için tek tabloda.

## 5b. İlk ölçüm sonuçları (21 Eki 2026)

Test seti: MediaSpeech TR'den ilk 300 dosya (ada göre sıralı), 72 dakika haber/TV konuşması. RTX 3060, float16, `beam_size=5`.
Komut: `python src/asr_olc.py data/mediaspeech_tr/TR --modeller small medium large-v3-turbo --vad acik kapali --sinir 300`

| Model | VAD | WER | CER | RTF |
|---|---|---|---|---|
| small (şu anki varsayılan) | açık | 19.6% | 9.2% | 0.048 |
| small | kapalı | 18.6% | 8.3% | 0.046 |
| medium | açık | 12.9% | 6.1% | 0.081 |
| medium | kapalı | 13.1% | 6.1% | 0.079 |
| **large-v3-turbo** | açık | **10.6%** | **5.9%** | **0.040** |
| large-v3-turbo | kapalı | 10.5% | 5.7% | 0.039 |

- **large-v3-turbo hem en doğru hem en hızlı:** `small`'a göre kelime hatası ~%46 daha az, gerçek zamandan ~25 kat hızlı.
  Turbo'nun decoder'ı 4 katman olduğu için `small`'dan bile hızlı çözüyor. → varsayılan model `large-v3-turbo` yapıldı (D-002).
- **VAD filtresi toplamda fark yaratmıyor** (10.6% / 10.5%). Bazı dosyalarda müzikli konuşmayı atıyor, ama canlı kullanımda
  sessizliği atlaması işe yarıyor; açık kalıyor, canlı testte tekrar bakılacak.
- Normalizasyon önemli: referanslar sayıları yazıyla yazıyor ("kırk"), Whisper rakamla ("40"). Rakamlar yazıya çevrilmeden önce
  WER turbo için 13.7%, small için 22.2% çıkıyordu; ~3 puanlık fark gerçek hata değil, yazım farkıydı.

### Tipik hatalar (turbo, en kötü dosyalar)

1. **Konuşmanın bir kısmı hiç yazılmıyor** (en büyük hata kaynağı). Dosya ortasında konuşmacı değişince veya araya müzik girince
   Whisper ilk ya da son cümleyi atlıyor (WER %77-87). Bir kısmı VAD'den (VAD kapatınca düzeliyor), bir kısmı Whisper'ın kendisinden.
   Toplantıda konuşmacı değişimi sık olduğu için **canlı testte izlenmeli**; parçaları kısa tutmak (kesici) bunu azaltır.
2. **Özel isimler:** "Kanuni" → "Kandone" (small), "Habertürk" → "haber fiktir", "Nazlıkul" → "Nazlı Kul". İnce ayar için iyi hedef.
3. **Konuşma dili / yazı dili farkı:** referans "aktarıcaz, olucak", Whisper "aktaracağız, olacak" yazıyor. Toplantı metni için
   Whisper'ınki daha kullanışlı; hata gibi görünse de sorun değil.
4. **Referans hataları:** MediaSpeech referansları bazen yanlış veya eksik (ör. referans "fener şenliği", Whisper doğru olarak
   "Şener Şen"). Bu yüzden WER'in bir kısmı gürültü; kendi toplantı kayıtlarımızla ayrıca ölçülmeli.
5. **Dosya kenarları:** MediaSpeech parçaları kelime ortasından kesilmiş; ilk/son kelime sık sık eksik.

## 6. İnce ayar (README'deki "fine-tuning ve karşılaştırma" maddesi)

- `large-v3-turbo` üzerinde LoRA (PEFT) ile Common Voice + ISSAI eğitimi; 12 GB kartta 8-bit + gradient checkpointing ile yapılabilir.
- Eğitilen model `ct2-transformers-converter` ile CTranslate2 formatına çevrilip faster-whisper'da kullanılır.
- Karşılaştırma: hazır model vs ince ayarlı model, MediaSpeech ve kendi kayıtlarımızda.

## Önerilen plan

1. **Ölçüm altyapısı:** test setleri, Türkçe normalizasyon, WER/CER/RTF tablosu; `small`, `medium`, `large-v3-turbo`, `large-v3` ve 1-2 Türkçe ince ayarlı model.
2. **Canlı prototip:** mikrofon + loopback → VAD → streaming politikası → kesinleşmiş metin parçaları; gecikme ölçümü.
3. **İnce ayar** ve karşılaştırma.

## 2. adımla arayüz (ekipçe karar verilmeli)

Önerilen çıktı biçimi, her kesinleşmiş parça için:

```python
@dataclass
class Segment:
    start: float      # saniye, toplantı başından itibaren
    end: float
    text: str
    language: str     # "tr"
    speaker: str      # "ben" / "karsi_taraf" (ses kaynağına göre)
    is_final: bool    # False: geçici sonuç, değişebilir
    source_id: int    # çeviri ve ses çıktısını kaynak parçaya bağlamak için
```

Tüm hat için bkz. [architecture.md](architecture.md) ve [D-003](decisions.md).

Çeviri yalnızca `is_final=True` parçaları işlerse çeviri tarafı kararsız metinle uğraşmaz.

## Açık sorular

- İlk sürümde sadece Türkçe konuşma mı, yoksa dil otomatik algılansın mı?
- Kabul edilebilir gecikme ne kadar (ör. < 2 s)?
- 2. adımın beklediği giriş biçimi yukarıdaki `Segment` ile uyuşuyor mu?

## Kaynaklar

- Whisper large-v3-turbo ve genel karşılaştırmalar: [Gladia](https://www.gladia.io/blog/best-open-source-speech-to-text-models), [Northflank](https://northflank.com/blog/best-open-source-speech-to-text-stt-model-in-2026-benchmarks), [OpenVox](https://openvoxai.com/blog/best-local-stt-transcription-models-2026)
- Türkçe ince ayarlı modeller: [selimc/whisper-large-v3-turbo-turkish](https://huggingface.co/selimc/whisper-large-v3-turbo-turkish), [erdiyalcin/whisper-large-v3-turkish-test1](https://huggingface.co/erdiyalcin/whisper-large-v3-turkish-test1)
- Qwen3-ASR: [GitHub](https://github.com/QwenLM/Qwen3-ASR), [model kartı](https://huggingface.co/Qwen/Qwen3-ASR-1.7B-hf), [teknik rapor](https://arxiv.org/html/2601.21337v1)
- Streaming: [ufal/whisper_streaming](https://github.com/ufal/whisper_streaming), [ufal/SimulStreaming](https://github.com/ufal/SimulStreaming), [WhisperLiveKit](https://github.com/QuentinFuxa/WhisperLiveKit), [WhisperLive (Docker)](https://github.com/hwdsl2/docker-whisper-live)
- Ses yakalama: [PyAudioWPatch](https://pypi.org/project/PyAudioWPatch/0.2.12.1), [SoundCard](https://soundcard.readthedocs.io/en/latest/)
- Veri: [Common Voice 25.0 TR](https://datacollective.mozillafoundation.org/datasets/cmn2e7kbl01k2mm07gm5n1bc9), [ISSAI Turkish Speech Corpus](https://huggingface.co/datasets/issai/Turkish_Speech_Corpus/blob/main/README.md), [MediaSpeech (OpenSLR 108)](https://openslr.org/108/)
