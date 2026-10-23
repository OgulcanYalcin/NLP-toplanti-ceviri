# Toplantılar için Simültane Çeviri ve Transkript

Çevrimiçi toplantılarda konuşulanları anlık olarak yazıya döken, başka bir dile çeviren
ve altyazı olarak gösteren bir uygulama. Toplantı sonunda iki dilli transkript kaydedilir.

NLP dersi projesi.

## Kullanılan modeller

| Görev | Model |
|---|---|
| Konuşma tanıma | [Whisper](https://github.com/openai/whisper) (faster-whisper ile) |
| Çeviri (TR → EN) | [Helsinki-NLP/opus-mt-tr-en](https://huggingface.co/Helsinki-NLP/opus-mt-tr-en) |

## Gereksinimler

- Windows
- Python 3.11
- NVIDIA ekran kartı (sürücüsü CUDA 13.2 veya üstünü desteklemeli; `nvidia-smi` ile kontrol edilebilir)

## Kurulum

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Çalıştırma

```powershell
python -u src/pipeline.py
```

Ses dosyası `data/` klasörüne konmalı ve `src/pipeline.py` içindeki `SES_DOSYASI` ayarı güncellenmeli.

## Konuşma tanıma ölçümü

Modelleri aynı test setinde karşılaştırır (WER, CER, RTF). Test seti: her ses dosyasının yanında aynı adlı `.txt`
referans metni olan bir klasör. Örnek veri: [MediaSpeech Türkçe](https://openslr.org/108/) (CC BY 4.0),
`data/` altına açılır.

```powershell
python src/asr_olc.py data/mediaspeech_tr/TR --modeller small large-v3-turbo --sinir 200
```

Sonuç `outputs/asr_olcum_<tarih>.md` (özet tablo + en çok hata yapılan dosyalar) ve `.csv` (dosya bazında) olarak yazılır.

Testler (GPU gerekmez): `python -m pytest`

## Proje durumu

- [x] Ses dosyasını yazıya dökme
- [x] Türkçe → İngilizce çeviri
- [x] Konuşma tanıma + çeviri pipeline'ı
- [ ] Canlı mikrofon girişi
- [ ] Altyazı ekranı
- [ ] Transkript kaydetme
- [ ] Modellerin ince ayarı (fine-tuning) ve karşılaştırma