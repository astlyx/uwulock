<p align="center">
  <img src="images/banner.png" alt="uwulock banner" width="600">
</p>

# UwULock Bot 🔒💕

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2)](https://discordpy.readthedocs.io/)

Arkadaşlarını "uwulock"layan, eğlence amaçlı bir Discord botu. Kilitlediğin
kişi mesaj attığında bot mesajını siler ve aynı isim/avatar ile
**uwu'laştırılmış** halini webhook üzerinden tekrar gönderir (mesajın
yanındaki "APP" etiketi webhook olduğunu gösterir).

> ⚠️ **Sorumlu kullanım**: Bu bot şaka amaçlıdır. Lütfen
> bunu istemeyen arkadaşlarınızla kullanmayın. Sunucu sahibi olmadığınız yerlerde veya rızası olmayan
> kişilerde kullanmayın.

## Özellikler

- Kilitli kişinin mesajlarını otomatik **uwu'laştırır** (l/r → w, kekeleme,
  kelime değişimleri, emoji ve aksiyon ifadeleri)
- Türkçe ve İngilizce kelime değişimleri (`değil` → `diil`, `love` → `wuv` vb.)
- Linkleri, kod bloklarını, mention ve özel emojileri **bozmaz**
- Mesaj **düzenlenirse** de yakalar
- Toplu kilitleme/açma (`!uwulockall`, `!uwuunlockall`)
- Skor tablosu (`!uwustats`) ve bot durumunda (presence) kaç kişinin kilitli
  olduğunu gösterme
- Tüm komutlar sadece bot sahibine (`OWNER_ID`) açık

## 1. Discord Bot Oluşturma

1. https://discord.com/developers/applications adresine git, **New Application**'a tıkla.
2. Sol menüden **Bot** sekmesine gir, **Reset Token** ile token'ı al (bunu kimseyle paylaşma!).
3. Aynı sayfada **Privileged Gateway Intents** kısmından şunları aç:
   - `MESSAGE CONTENT INTENT`
   - `SERVER MEMBERS INTENT`

## 2. Botu Sunucuya Davet Etme

1. Sol menüden **OAuth2 → URL Generator**'a gir.
2. **Scopes**: `bot`
3. **Bot Permissions**:
   - Manage Webhooks
   - Manage Messages
   - View Channels
   - Send Messages
   - Read Message History
   - Embed Links
   - Attach Files
4. Oluşan linki tarayıcıda aç ve botu sunucuna ekle.

## 3. Kurulum

```bash
pip install -r requirements.txt
```

Aynı klasörde bir `.env` dosyası oluştur ve şunları yaz:

```
DISCORD_BOT_TOKEN=buraya_token_gelecek
OWNER_ID=senin_discord_kullanici_idn
```

**Discord ID'ni nasıl bulursun?**
1. Discord → Ayarlar → Gelişmiş (Advanced) → **Geliştirici Modu**'nu aç.
2. Kendi profiline sağ tıkla → **Kullanıcı Kimliğini Kopyala** (Copy User ID).
3. Bu sayıyı `OWNER_ID` olarak yapıştır.

(İstersen `.env` yerine ortam değişkeni olarak da ayarlayabilirsin.)

## 4. Çalıştırma

```bash
python uwulock_bot.py
```

## Komutlar (varsayılan prefix: `!`)

> ⚠️ Tüm komutlar **sadece `OWNER_ID` ile eşleşen kişi** tarafından
> kullanılabilir. Başka biri komut yazarsa bot hiçbir cevap vermez —
> komutların var olduğu bile fark edilmez.

| Komut | Açıklama |
|---|---|
| `!uwulock @kişi` | Kişiyi kilitler, mesajları otomatik uwu'laşır |
| `!uwuunlock @kişi` (`!kapat @kişi`) | O kişinin kilidini kaldırır |
| `!uwulockall` | Sunucudaki herkesi kilitler (sahip ve botlar hariç) |
| `!uwuunlockall` | Sunucudaki tüm kilitleri kaldırır |
| `!uwulist` | Kilitli kişileri listeler |
| `!uwuify <metin>` | Metni test amaçlı uwu'laştırır |
| `!uwustats` | Kim kaç kez uwulandı, skor tablosunu gösterir |
| `!uwustatus <durum>` | Botun durumunu değiştirir: `online`, `idle`, `invisible`, `dnd` |
| `!uwuhelp` | Komut listesini gösterir |
| `!botukapat` (`!shutdown`) | **Botun kendisini** tamamen kapatır |

## Nasıl Çalışıyor?

- Kilitli kişi mesaj attığında, bot orijinal mesajı siler.
- O kanalda kendine ait bir webhook oluşturur (yoksa).
- Webhook üzerinden, kişinin **adı ve avatarıyla** uwu'laştırılmış mesajı
  gönderir. Bu sayede mesaj sanki o kişi öyle yazmış gibi görünür ama
  "UYG"/"APP" etiketiyle webhook olduğu da anlaşılır.
- `!` ile başlayan mesajlar (komutlar) uwu'laştırılmaz. Ama unutma: komutlara
  sadece `OWNER_ID` cevap alabilir, kilitli kişi `!uwuunlock` yazsa da bot ona
  cevap vermez/kilidi açmaz.
- Linkler, ` ```kod bloğu``` `/`` `satır içi kod` ``, Discord mention'ları
  (`<@...>`, `<#...>`), özel emojiler (`<:isim:id>`) ve zaman damgaları
  (`<t:...>`) uwuify'dan **etkilenmez**, olduğu gibi korunur.
- Bot, kilitli birinin her mesajını saydırır; `!uwustats` ile kim kaç kez
  uwulandığını gösteren bir skor tablosu görebilirsin.
- Kilitli biri mesajını **düzenlerse** (edit), bot bunu da yakalar: eski
  mesajı silip düzenlenmiş hâlini uwu'laştırılmış olarak tekrar gönderir.
- Bot, "durumunda" (presence/activity) kaç kişinin şu anda kilitli olduğunu
  `👀 X kişi uwulandı 💕` şeklinde gösterir. Bu sayı tüm sunuculardaki
  toplam kilitli kişi sayısıdır.
- `!uwustatus online|idle|invisible|dnd` ile botun Discord üzerindeki
  görünürlük durumunu değiştirebilirsin. `invisible` seçilirse bot çevrimdışı
  görünür ama arka planda çalışmaya devam eder.

## Notlar / Sınırlamalar

- Bot, mesajları silebilmesi için **Manage Messages**, taklit mesaj
  gönderebilmesi için **Manage Webhooks** yetkisine sahip olmalı.
- Kilit listesi ve istatistikler `uwulock_data.json` dosyasında saklanır, bot
  yeniden başlatılsa da kaybolmaz. Dosyanın yapısı:
  ```json
  {
    "locks": {"sunucu_id": [kullanici_id, ...]},
    "stats": {"sunucu_id": {"kullanici_id": kac_kez_uwulandi}}
  }
  ```
- Uwuify fonksiyonu rastgele çalışır: harfleri "w"ya çevirir, kekeleme ekler
  (`m-m-m-`), aralara `uwu`/`owo`/`*utanarak başka tarafa bakar*` gibi
  ifadeler ve emoji serpiştirir. `!uwuify` komutuyla istediğin kadar test
  edebilirsin.

## Katkıda Bulunma

Pull request'lere açığız! Özellikle:
- `WORD_SUBSTITUTIONS` sözlüğüne yeni kelime/dil ekleme
- `FACES` listesine yeni ifadeler ekleme
- Yeni komutlar veya iyileştirmeler

Büyük bir değişiklik yapmadan önce bir issue açıp tartışmak iyi olur.

## Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.

