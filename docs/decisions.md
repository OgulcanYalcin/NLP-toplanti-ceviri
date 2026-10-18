# Kararlar

En yeni üstte. Durum: **öneri** (ekip onaylayana kadar) veya **kabul**.

### D-004 · v1'de her istemci tüm hattı kendi çalıştırır · öneri · 18 Eki 2026
- **Karar:** bir istemci = bir dil çifti = tek süreçte ses yakalama + ASR + MT + TTS.
- **Neden:** en basit yapı; demo için tek dil çifti yeterli. Paylaşılan ASR sunucusu çoklu istemci uç adımına bırakıldı.
- **Reddedilen:** baştan istemci-sunucu yapısı (WebSocket, oturum yönetimi) v1 için gereksiz iş çıkarır.
- **Not:** ortak transkript havuzu ve kişisel ses hedefiyle sunucu yapısı yeniden tartışılıyor; bkz. [architecture.md](architecture.md#tartışılacak-sunucu-mu-istemci-mi).

### D-003 · Aşamalar `Segment` ile konuşur, çeviri yalnızca kesinleşmiş parçaları işler · öneri · 18 Eki 2026
- **Karar:** ASR, MT ve TTS ortak `Segment` veri sınıfını alıp verir; `is_final=False` parçalar sadece ekranda geçici gösterilir.
- **Neden:** her adımın sahibi diğerlerinden bağımsız çalışıp test edebilir. Çeviri, sürekli değişen yarım cümlelerle uğraşmaz.
- **Reddedilen:** düz metin geçirmek (zaman damgası ve konuşmacı kaybolur, transkript eşlenemez); geçici parçaları da çevirmek (çeviri titrer, GPU boşa harcanır).

### D-002 · ASR için faster-whisper, varsayılan model `large-v3-turbo` · öneri · 18 Eki 2026
- **Karar:** faster-whisper motoru korunur; varsayılan model `small`'dan `large-v3-turbo`'ya çıkar. Kesin model ölçümden sonra seçilir.
- **Neden:** turbo, large-v3'e yakın doğrulukta ve canlı kullanım için yeterince hızlı; 12 GB GPU'ya rahat sığar.
  faster-whisper zaten kurulu ve streaming kütüphanelerinin önerdiği backend.
- **Reddedilen:** `large-v3` (canlı kullanım için yavaş), Qwen3-ASR (Türkçe sonucu yayımlanmamış, ölçüm listesinde kalıyor). Ayrıntı: [asr-research.md](asr-research.md).

### D-001 · İlk dil çifti Türkçe → İngilizce · öneri · 18 Eki 2026
- **Karar:** v1 ve demo TR → EN ile yapılır; diğer çiftler (ör. DE → EN) uç adım.
- **Neden:** mevcut kod bu çift için çalışıyor; ekip Türkçe konuştuğu için test kaydı toplamak ve çıktıyı kontrol etmek kolay;
  `opus-mt-tr-en` hazır.
- **Reddedilen:** EN → TR ile başlamak (Türkçe toplantı kaydı bizim için daha kolay toplanır, Türkçe ASR dersin odağında).
