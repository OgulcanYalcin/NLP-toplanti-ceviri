# Mimari

Durum: **taslak, ekip onayı bekliyor** (18 Eki 2026).

## Genel akış (bir istemci, ör. TR → EN)

```
 mikrofon ─┐
           ├─> ses yakalama ─> VAD / bölütleme ─> [1] ASR ─> Segment(tr) ─> [2] MT ─> Segment(en) ─┬─> altyazı
 loopback ─┘   16 kHz mono                         faster-whisper            MarianMT               ├─> [3] TTS ─> hoparlör
                                                                                                    └─> transkript (TR + EN)
```

1. **Ses yakalama:** mikrofon (`sounddevice`) ve sistem sesi (WASAPI loopback, `PyAudioWPatch`) ayrı akışlar olarak,
   16 kHz mono float32'ye çevrilip kısa bloklar (ör. 0,5 s) halinde kuyruğa yazılır. Kaynak, konuşmacı bilgisi olarak taşınır.
2. **VAD / bölütleme:** Silero VAD konuşma olmayan kısımları atar, konuşmayı parçalara böler.
3. **[1] ASR:** streaming Whisper (faster-whisper, varsayılan `large-v3-turbo`). Geçici sonuçlar `is_final=False`,
   kesinleşen cümleler `is_final=True` olarak yayımlanır. Ayrıntılar: [asr-research.md](asr-research.md).
4. **[2] MT:** yalnızca `is_final=True` parçaları çevirir (şu an `Helsinki-NLP/opus-mt-tr-en`).
5. **[3] TTS:** çevrilen cümleyi seslendirir (model seçimi adım 3'ün sahibinde).
6. **Çıktılar:** altyazı penceresi (kaynak + çeviri), toplantı sonunda `outputs/` altına zaman damgalı transkript.

Her aşama ayrı bir iş parçacığında (thread) çalışır ve bir sonrakiyle `queue.Queue` üzerinden konuşur.
Böylece ASR bir parçayı işlerken ses yakalama ve çeviri beklemez; yavaş aşama da kuyruğun uzamasından hemen görülür.

## Aşamalar arası veri

```python
@dataclass
class Segment:
    start: float      # saniye, toplantı başından itibaren
    end: float
    text: str
    language: str     # "tr", "en", ...
    speaker: str      # "ben" | "karsi_taraf" (ses kaynağına göre)
    is_final: bool    # False: geçici sonuç, değişebilir
    source_id: int    # çeviri ve ses çıktısını kaynak parçaya bağlamak için
```

Her aşama `Segment` alır ve `Segment` verir; MT çıktısı aynı `source_id` ile hedef dilde yeni bir `Segment`'tir.
Transkript, aynı `source_id`'li kaynak ve çeviri parçalarını yan yana yazar.

## Önerilen klasör yapısı

```
src/
  ortak/       segment.py, ayarlar.py (model adları, cihaz, dil çifti tek yerde), cuda_ayar.py
  ses/         yakalama.py (mikrofon + loopback), vad.py
  asr/         streaming.py                        # adım 1
  ceviri/      cevirmen.py                         # adım 2
  seslendirme/ tts.py                              # adım 3
  arayuz/      altyazi.py
  istemci.py   bir dil çifti için tüm hattı kurar ve çalıştırır
degerlendirme/ wer.py, bleu.py, gecikme.py
docs/
```

Mevcut `transcribe.py`, `translate.py`, `pipeline.py` bu yapıya taşınana kadar olduğu gibi kalır.

## Çoklu istemci (uç adım)

v1'de her istemci kendi ASR modelini yükler. Birden fazla istemcide aynı ses tekrar tekrar yazıya dökülür ve
GPU belleği yetmez. Bu yüzden sonraki adımda:

- **Kaynak dil başına tek ASR** (sunucu), çıkan `Segment`'ler WebSocket ile istemcilere yayılır.
- Her istemci yalnızca kendi **MT + TTS**'ini çalıştırır.

WhisperLiveKit / WhisperLive bu sunucu yapısını hazır sunuyor; v1'deki `Segment` arayüzü korunursa geçiş istemci kodunu değiştirmez.

## Tartışılacak: sunucu mu, istemci mi?

Hedef ürün: herkes kendi bilgisayarında uygulamayı açar, her istemci yalnızca **kendi mikrofonunu** yazıya döker
(konuşmacı bilgisi bedavaya gelir), konuşmalar ortak bir transkript havuzuna düşer ve her dinleyici onları kendi dilinde,
konuşanın sesiyle duyar. Ağır işin nerede yapılacağı henüz kararlaştırılmadı.

| | Her şey istemcide (D-004) | Sunucuda (istemci: yakalama, VAD, yankı önleme, çalma, altyazı) |
|---|---|---|
| Donanım | Her kullanıcıda NVIDIA GPU gerekir | Tek GPU yeter, istemci herhangi bir dizüstü olabilir |
| Tekrarlanan iş | Her istemci aynı konuşmayı tekrar çevirip seslendirir | Çeviri ve seslendirme hedef dil başına bir kez, aynı dili isteyen herkese gönderilir |
| Ağ | Gerekmez (havuz hariç) | Her yön ~50-150 ms ek gecikme; ses yükü küçük |
| Gizlilik | Ses bilgisayardan çıkmaz | Toplantı sesi ve ses profilleri sunucuya gider: onay, TLS, silme seçeneği gerekir |
| Risk | Bir istemci çökerse sadece o etkilenir | Sunucu düşerse herkes etkilenir (demo riski) |
| İş yükü | Basit | WebSocket, oda/oturum yönetimi, yeniden bağlanma |

`Segment` arayüzü iki yapıda da aynı kalır; sadece kuyruk yerine WebSocket ile taşınır.

### Sunucuyu nerede çalıştırırız? (ücretsiz)

Bu bir son kullanıcı ürünü değil, bitmiş bir fikir / demo. Sunucunun 7/24 açık olması gerekmez; sadece test oturumlarında
ve demoda birkaç saat çalışır. Bu yüzden ücretsiz seçenekler yeterli:

| Seçenek | Kullanım | Not |
|---|---|---|
| Geliştirme bilgisayarı (RTX 3060 12 GB) | Varsayılan: geliştirme, testler, demo | Sunucu gerektiğinde başlatılır; ekip Tailscale (ücretsiz) ile farklı ağlardan bağlanır. 3-5 kullanıcı ve 2-3 dil için yeterli görünüyor |
| Modal (aylık ~$30 ücretsiz kredi) | Bulut yedeği, demo | GPU'lu WebSocket uç noktası; boşta kapanır, sadece toplantı süresince harcar. Modellerin yüklenmesi için toplantıdan ~1 dk önce başlatılır |
| Kaggle / Colab (ücretsiz GPU) | İnce ayar ve değerlendirme koşuları; gerekirse kısa testler | Not defteri ortamı; sunucu için tünel (cloudflared, ngrok) gerekir ve bağlantı kopabilir. Notlandırılan demo için önerilmez |
| Üniversitedeki RTX 5080 (16 GB) | Demo günü | Sürekli kullanım için değil, demo için rezerve edilir |

Demoda sunucunun tek hata noktası olma riskine karşı: geliştirme bilgisayarı ve Modal ikisi de hazır tutulur, biri düşerse diğeri açılır.

## Gecikme bütçesi (hedef < 3 s)

| Aşama | Hedef |
|---|---|
| Ses bloğu + VAD | ~0,5 s |
| ASR (kesinleşme dahil) | ~1,5 s |
| MT | ~0,3 s |
| Altyazı | ~0 |
| TTS (ilk ses) | ~0,5 s (altyazıyı geciktirmez) |

Her aşama giriş ve çıkış zamanını `Segment`'e işler; `degerlendirme/gecikme.py` bunlardan ortalama ve p90 çıkarır.
