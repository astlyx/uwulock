import os
import re
import json
import random

import discord
from discord.ext import commands

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------- AYARLAR ----------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
PREFIX = "!"
DATA_FILE = "uwulock_data.json"
WEBHOOK_NAME = "UwULock"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)


@bot.check
async def sadece_sahip(ctx: commands.Context) -> bool:
    """Bot komutlarını sadece OWNER_ID'ye sahip kişi kullanabilir."""
    return ctx.author.id == OWNER_ID


# ---------------- VERİ (KİLİTLİ KULLANICILAR + İSTATİSTİK) ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    if "locks" not in data and "stats" not in data:
        # Eski format: doğrudan {guild_id: [user_id, ...]} - taşıyalım
        data = {"locks": data, "stats": {}}
    else:
        data.setdefault("locks", {})
        data.setdefault("stats", {})

    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


locked_data = load_data()
# locked_data["locks"] -> {"guild_id": [user_id, ...]}
# locked_data["stats"] -> {"guild_id": {"user_id": kac_kez_uwulandi}}


def is_locked(guild_id: int, user_id: int) -> bool:
    return user_id in locked_data["locks"].get(str(guild_id), [])


def lock_user(guild_id: int, user_id: int):
    key = str(guild_id)
    locked_data["locks"].setdefault(key, [])
    if user_id not in locked_data["locks"][key]:
        locked_data["locks"][key].append(user_id)
        save_data(locked_data)


def unlock_user(guild_id: int, user_id: int):
    key = str(guild_id)
    if user_id in locked_data["locks"].get(key, []):
        locked_data["locks"][key].remove(user_id)
        save_data(locked_data)


def lock_users_bulk(guild_id: int, user_ids) -> int:
    """Birden fazla kullanıcıyı tek seferde kilitler, kaç yeni kişi eklendiğini döner."""
    key = str(guild_id)
    locked_data["locks"].setdefault(key, [])
    added = 0
    for uid in user_ids:
        if uid not in locked_data["locks"][key]:
            locked_data["locks"][key].append(uid)
            added += 1
    if added:
        save_data(locked_data)
    return added


def unlock_all(guild_id: int) -> int:
    """Sunucudaki tüm kilitleri kaldırır, kaç kişinin kilidinin kalktığını döner."""
    key = str(guild_id)
    removed = len(locked_data["locks"].get(key, []))
    if removed:
        locked_data["locks"][key] = []
        save_data(locked_data)
    return removed


def increment_stat(guild_id: int, user_id: int):
    gkey, ukey = str(guild_id), str(user_id)
    locked_data["stats"].setdefault(gkey, {})
    locked_data["stats"][gkey][ukey] = locked_data["stats"][gkey].get(ukey, 0) + 1
    save_data(locked_data)


def get_stats(guild_id: int, limit: int = 10):
    gkey = str(guild_id)
    stats = locked_data["stats"].get(gkey, {})
    return sorted(stats.items(), key=lambda item: item[1], reverse=True)[:limit]


# ---------------- PRESENCE (BOT DURUMU) ----------------
STATUS_MAP = {
    "online": discord.Status.online,
    "çevrimiçi": discord.Status.online,
    "idle": discord.Status.idle,
    "boşta": discord.Status.idle,
    "invisible": discord.Status.invisible,
    "görünmez": discord.Status.invisible,
    "dnd": discord.Status.dnd,
    "rahatsız etmeyin": discord.Status.dnd,
}

# Bot yeniden başladığında varsayılan durum (istersen değiştir)
current_status = discord.Status.online


def total_locked_count() -> int:
    return sum(len(v) for v in locked_data["locks"].values())


async def update_presence():
    total = total_locked_count()
    if total == 0:
        text = "kimse uwulanmadı 💔"
    elif total == 1:
        text = "1 kişi uwulandı 💕"
    else:
        text = f"{total} kişi uwulandı 💕"
    activity = discord.Activity(type=discord.ActivityType.watching, name=text)
    await bot.change_presence(status=current_status, activity=activity)


# ---------------- UWUIFY ----------------
FACES = [
    "uwu", "owo", "OwO", "UwU", ">w<", ":3", "nya~", "rawr x3", "(´｡• ᵕ •｡`)",
    "*utanarak başka tarafa bakar*",
    "*kıkırdar*",
    "*kuyruğunu sallar*",
    "*yanaklarını şişirir*",
    "*saklanır*",
    "*mahcup olur*",
    "*gözlerini kaçırır*",
    "*sevinçle zıplar*",
    "*pati atar*",
    "*mırıldanır*",
    "*surat yapar*",
    "*elleriyle yüzünü kapatır*",
]

EMOJIS = ["🥺", "💕", "✨", "🌸", "💖", "😳", "🐾", "💗", "✧"]

# Bunlar uwuify edilmeden korunacak: kod blokları, linkler, Discord
# mention/emoji/zaman damgası syntax'ı. Aksi halde linkler kırılır,
# özel emojiler bozulur.
PROTECTED_PATTERN = re.compile(
    r"```.*?```"                 # ```kod bloğu```
    r"|`[^`\n]*`"                # `satır içi kod`
    r"|https?://\S+"             # http(s) linki
    r"|www\.\S+"                 # www linki
    r"|<a?:\w+:\d+>"              # <:özel_emoji:12345>
    r"|<@!?\d+>"                  # <@kullanıcı>
    r"|<@&\d+>"                   # <@&rol>
    r"|<#\d+>"                    # <#kanal>
    r"|<t:\d+(?::[tTdDfFR])?>",   # <t:zaman_damgası>
    re.DOTALL,
)

# Kelime değişimleri: anahtar kelimeler küçük harfle yazılmalı
WORD_SUBSTITUTIONS = {
    # İngilizce
    "love": "wuv",
    "cute": "kawaii",
    "friend": "fwend",
    "friends": "fwends",
    "small": "smol",
    "this": "dis",
    "that": "dat",
    "the": "da",
    "hello": "hewwo",
    "world": "wowld",
    "what": "wat",
    "stupid": "baka",
    "please": "pwease",
    "because": "bcuz",
    "with": "wif",
    "good": "gud",
    "dog": "doggo",
    "cat": "kitty",
    "big": "beeg",
    "yes": "yus",
    "not": "nawt",
    # Türkçe
    "değil": "diil",
    "değilim": "diilim",
    "değildir": "diildir",
    "tamam": "tamaaawm",
    "evet": "eveet",
    "abi": "abicim",
    "abla": "ablacım",
    "kanka": "kankacım",
    "ya": "yiaaa",
    "yok": "yokk",
    "çok": "çokk",
    "iyi": "iyii",
    "kötü": "kötüüü",
}

_WORD_SUB_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in WORD_SUBSTITUTIONS) + r")\b",
    re.IGNORECASE,
)


def substitute_words(text: str) -> str:
    def repl(match):
        word = match.group(0)
        replacement = WORD_SUBSTITUTIONS[word.lower()]
        if word.isupper():
            return replacement.upper()
        if word[0].isupper():
            return replacement.capitalize()
        return replacement

    return _WORD_SUB_PATTERN.sub(repl, text)


def uwuify(text: str) -> str:
    if not text:
        return text

    # link/kod/mention/emoji gibi kısımları korumaya al
    protected = []

    def protect(match):
        protected.append(match.group(0))
        return f"§{len(protected) - 1}§"

    text = PROTECTED_PATTERN.sub(protect, text)

    # kelime değişimleri: love->wuv, cute->kawaii, friend->fwend, small->smol vb.
    text = substitute_words(text)

    # l/r -> w (büyük/küçük harf korunarak)
    def lr_to_w(match):
        ch = match.group(0)
        return "W" if ch in "LR" else "w"

    text = re.sub(r"[lrLR]", lr_to_w, text)

    # "na, ne, ni, no, nu" -> "nya, nye, nyi, nyo, nyu"
    def nasal(match):
        g = match.group(0)
        return g[0] + "y" + g[1:]

    text = re.sub(r"[nN][aeiouAEIOU]", nasal, text)

    # bazı kelimelere kekeleme ekle: "making" -> "m-m-m-making"
    words = text.split(" ")
    new_words = []
    for word in words:
        if word and word[0].isalpha() and random.random() < 0.35:
            n = random.randint(1, 3)
            stutter = "-".join([word[0]] * n)
            word = f"{stutter}-{word}"
        new_words.append(word)

    # araya rastgele bir ifade ekle
    if new_words and random.random() < 0.6:
        pos = random.randint(0, len(new_words))
        new_words.insert(pos, f"({random.choice(FACES)})")

    # araya rastgele emoji(ler) serpiştir
    if new_words and random.random() < 0.6:
        for _ in range(random.randint(1, 2)):
            pos = random.randint(0, len(new_words))
            new_words.insert(pos, random.choice(EMOJIS))

    text = " ".join(new_words)

    # sona ekleme
    if random.random() < 0.7:
        text += " " + random.choice(FACES)

    # korunan kısımları (link, kod, mention, emoji) geri koy
    def restore(match):
        idx = int(match.group(1))
        if 0 <= idx < len(protected):
            return protected[idx]
        return match.group(0)

    text = re.sub(r"§(\d+)§", restore, text)

    return text[:2000]  # Discord mesaj limiti


# ---------------- WEBHOOK İLE TAKLİT MESAJ ----------------
async def get_or_create_webhook(channel: discord.TextChannel) -> discord.Webhook:
    webhooks = await channel.webhooks()
    for wh in webhooks:
        if wh.name == WEBHOOK_NAME and wh.user == bot.user:
            return wh
    return await channel.create_webhook(name=WEBHOOK_NAME)


async def mimic_message(message: discord.Message):
    increment_stat(message.guild.id, message.author.id)

    content = message.content
    uwu_text = uwuify(content) if content else None

    files = []
    for attachment in message.attachments:
        try:
            files.append(await attachment.to_file())
        except Exception:
            pass

    channel = message.channel
    thread = None
    if isinstance(channel, discord.Thread):
        thread = channel
        channel = channel.parent

    if channel is None:
        return

    try:
        webhook = await get_or_create_webhook(channel)
    except discord.Forbidden:
        return

    try:
        await message.delete()
    except (discord.Forbidden, discord.NotFound):
        pass

    send_kwargs = dict(
        content=uwu_text,
        username=message.author.display_name,
        avatar_url=message.author.display_avatar.url,
        files=files,
    )
    if thread is not None:
        send_kwargs["thread"] = thread

    try:
        await webhook.send(**send_kwargs)
    except discord.HTTPException:
        pass


# ---------------- EVENTLER ----------------
@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı, uwulamaya hazır.")
    await update_presence()


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.guild and is_locked(message.guild.id, message.author.id):
        if not message.content.startswith(PREFIX):
            await mimic_message(message)
            return

    await bot.process_commands(message)


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if after.author.bot:
        return

    # Discord bazen link önizlemesi (embed) eklerken de bu eventi tetikler,
    # metin aynıysa görmezden gel.
    if before.content == after.content:
        return

    if after.guild and is_locked(after.guild.id, after.author.id):
        if not after.content.startswith(PREFIX):
            # Mesaj düzenlendi: eskisini sil, düzenlenmiş hâlini uwu'laştırıp gönder
            await mimic_message(after)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        # Sadece bot sahibi kullanabilir, başkasına bir şey gösterme
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Bu komutu kullanmak için yetkin yok! 😤")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Böyle bir üye bulamadım.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"Eksik parametre. Kullanım: `{PREFIX}{ctx.command} {ctx.command.signature}`"
        )
    else:
        raise error


# ---------------- KOMUTLAR ----------------
@bot.command(name="uwulock")
async def uwulock_cmd(ctx, member: discord.Member):
    if member.id == bot.user.id:
        await ctx.send("Beni uwulocklayamazsın 😤")
        return
    if member.bot:
        await ctx.send("Botları uwulocklayamazsın.")
        return
    lock_user(ctx.guild.id, member.id)
    await update_presence()
    await ctx.send(f"🔒 {member.mention} artık **uwulock**landı! UwU")


@bot.command(name="uwuunlock", aliases=["kapat"])
async def uwuunlock_cmd(ctx, member: discord.Member):
    unlock_user(ctx.guild.id, member.id)
    await update_presence()
    await ctx.send(f"🔓 {member.mention} serbest kaldı. (şimdilik)")


@bot.command(name="uwulockall")
async def uwulockall_cmd(ctx):
    targets = [
        m.id for m in ctx.guild.members
        if not m.bot and m.id != OWNER_ID and m.id != bot.user.id
    ]
    added = lock_users_bulk(ctx.guild.id, targets)
    await update_presence()
    await ctx.send(
        f"🔒 Sunucudaki **{added}** kişi **uwulocklandı!** Artık herkes UwU konuşacak~ "
        f"*kuyruğunu sallar*"
    )


@bot.command(name="uwuunlockall")
async def uwuunlockall_cmd(ctx):
    removed = unlock_all(ctx.guild.id)
    await update_presence()
    if removed == 0:
        await ctx.send("Zaten kilitli kimse yoktu.")
        return
    await ctx.send(f"🔓 **{removed}** kişinin kilidi kaldırıldı. Özgürlük!")


@bot.command(name="uwulist")
async def uwulist_cmd(ctx):
    ids = locked_data["locks"].get(str(ctx.guild.id), [])
    if not ids:
        await ctx.send("Şu an kimse kilitli değil.")
        return
    mentions = ", ".join(f"<@{uid}>" for uid in ids)
    await ctx.send(f"Kilitli kullanıcılar: {mentions}")


@bot.command(name="uwuify")
async def uwuify_cmd(ctx, *, text: str):
    await ctx.send(uwuify(text))


@bot.command(name="uwustats")
async def uwustats_cmd(ctx):
    stats = get_stats(ctx.guild.id)
    if not stats:
        await ctx.send("Henüz kimse uwulanmamış... şimdilik. 😏")
        return

    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (user_id, count) in enumerate(stats):
        prefix = medals[i] if i < len(medals) else f"`{i + 1}.`"
        lines.append(f"{prefix} <@{user_id}> — **{count}** kez uwulandı")

    embed = discord.Embed(
        title="UwU Skor Tablosu 🏆",
        description="\n".join(lines),
        color=discord.Color.pink(),
    )
    await ctx.send(embed=embed)


@bot.command(name="uwuhelp")
async def uwuhelp_cmd(ctx):
    embed = discord.Embed(
        title="UwULock Bot Komutları",
        description=(
            f"`{PREFIX}uwulock @kişi` - Kişiyi uwulocklar\n"
            f"`{PREFIX}uwuunlock @kişi` (`{PREFIX}kapat @kişi`) - Kilidi açar\n"
            f"`{PREFIX}uwulockall` - Sunucudaki herkesi uwulocklar (sahip hariç)\n"
            f"`{PREFIX}uwuunlockall` - Sunucudaki tüm kilitleri kaldırır\n"
            f"`{PREFIX}uwulist` - Kilitli kişileri listeler\n"
            f"`{PREFIX}uwuify <metin>` - Metni uwu'laştırır (test için)\n"
            f"`{PREFIX}uwustats` - UwU skor tablosunu gösterir\n"
            f"`{PREFIX}uwustatus <durum>` - Bot durumunu değiştirir "
            f"(online/idle/invisible/dnd)\n"
            f"`{PREFIX}botukapat` - Botun kendisini tamamen kapatır\n\n"
            "⚠️ Bu komutlar sadece bot sahibi tarafından kullanılabilir.\n"
            "💡 Bot, kaç kişinin kilitli olduğunu \"şu kadar kişi uwulandı\" "
            "şeklinde durumunda (presence) gösterir."
        ),
        color=discord.Color.pink(),
    )
    await ctx.send(embed=embed)


@bot.command(name="botukapat", aliases=["shutdown"])
async def botukapat_cmd(ctx):
    await ctx.send("Bot tamamen kapatılıyor...")
    await bot.close()


@bot.command(name="uwustatus")
async def uwustatus_cmd(ctx, durum: str):
    global current_status

    durum_key = durum.lower()
    if durum_key not in STATUS_MAP:
        gecerli = ", ".join(sorted(set(STATUS_MAP.keys())))
        await ctx.send(f"Geçersiz durum. Kullanabileceklerin: {gecerli}")
        return

    current_status = STATUS_MAP[durum_key]
    await update_presence()
    await ctx.send(f"✅ Bot durumu **{durum}** olarak ayarlandı.")


# ---------------- BAŞLAT ----------------
if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError(
            "DISCORD_BOT_TOKEN ayarlanmamış! .env dosyasına ya da ortam değişkenine ekle."
        )
    if OWNER_ID == 0:
        raise RuntimeError(
            "OWNER_ID ayarlanmamış! .env dosyasına Discord kullanıcı ID'ni ekle."
        )
    bot.run(TOKEN)
