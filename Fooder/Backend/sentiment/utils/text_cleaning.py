"""
text_cleaning.py
================
Utilitas pembersihan teks untuk review bahasa Indonesia.
Digunakan oleh sentiment_service dan review_service.
"""

import re
import string


# ── Stopwords Indonesia (subset penting) ──────────────────────────────────────
STOPWORDS_ID = {
    "yang", "di", "dan", "ke", "dari", "ini", "itu", "dengan", "untuk",
    "pada", "adalah", "tidak", "ada", "juga", "saya", "kami", "kita",
    "mereka", "dia", "nya", "ya", "jadi", "kalau", "karena", "tapi",
    "atau", "sudah", "belum", "bisa", "akan", "seperti", "lebih", "sangat",
    "sekali", "aja", "sih", "deh", "dong", "lah", "kan", "lagi", "sudah",
    "nih", "si", "ga", "gak", "ngga", "enggak", "nggak", "banget",
    "bgt", "udah", "udh", "emang", "memang", "pun", "punya", "buat",
    "sama", "mau", "maka", "juga", "oleh", "saat", "bila", "ketika",
    "setelah", "sebelum", "hingga", "sampai", "bahwa", "agar", "supaya",
}

# ── Normalisasi kata slang/singkatan ──────────────────────────────────────────
SLANG_DICT = {
    "gak": "tidak", "ga": "tidak", "ngga": "tidak", "nggak": "tidak",
    "enggak": "tidak", "tdk": "tidak", "g": "tidak",
    "udah": "sudah", "udh": "sudah", "dah": "sudah",
    "bgt": "banget", "bngt": "banget",
    "enak": "enak", "enk": "enak",
    "bagus": "bagus", "bgs": "bagus",
    "jelek": "jelek", "jlk": "jelek",
    "mhl": "mahal", "murah": "murah", "mrh": "murah",
    "lmyn": "lumayan", "lmayan": "lumayan",
    "ok": "oke", "oke": "oke", "okelah": "oke",
    "recommended": "rekomendasi", "recommend": "rekomendasi",
    "worth": "sebanding", "worthit": "sebanding",
    "porsi": "porsi", "pors": "porsi",
    "rasa": "rasa", "rasanya": "rasa",
    "pelayanan": "pelayanan", "service": "pelayanan",
    "tempatnya": "tempat", "tempatny": "tempat",
    "makanannya": "makanan", "makananny": "makanan",
    "harganya": "harga", "hargany": "harga",
    "mantap": "mantap", "mntap": "mantap", "mantul": "mantap",
    "kece": "bagus", "keren": "bagus",
    "pedes": "pedas", "pedes": "pedas",
}


def normalize_slang(text: str) -> str:
    """Ganti kata slang dengan kata baku."""
    words = text.split()
    return " ".join(SLANG_DICT.get(w, w) for w in words)


def remove_emoji(text: str) -> str:
    """Hapus emoji dari teks."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text)


def clean_text(text: str, remove_stopwords: bool = False) -> str:
    """
    Pipeline pembersihan teks utama.

    Steps:
        1. Lowercase
        2. Hapus URL
        3. Hapus mention & hashtag
        4. Hapus emoji
        5. Hapus angka
        6. Hapus tanda baca
        7. Normalisasi spasi
        8. Normalisasi slang
        9. (Opsional) Hapus stopwords
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)          # hapus URL
    text = re.sub(r"@\w+|#\w+", "", text)               # hapus mention/hashtag
    text = remove_emoji(text)                            # hapus emoji
    text = re.sub(r"\d+", "", text)                     # hapus angka
    text = text.translate(str.maketrans("", "", string.punctuation))  # hapus tanda baca
    text = re.sub(r"\s+", " ", text).strip()            # normalisasi spasi
    text = normalize_slang(text)                         # normalisasi slang

    if remove_stopwords:
        words = text.split()
        text = " ".join(w for w in words if w not in STOPWORDS_ID)

    return text


def tokenize(text: str) -> list[str]:
    """Tokenisasi sederhana berbasis spasi."""
    return text.split()


def simple_stem(word: str) -> str:
    """
    Stemming sederhana (fallback tanpa Sastrawi).
    Untuk stemming penuh, gunakan Sastrawi di sentiment_service.
    """
    prefixes = ["me", "di", "ke", "se", "ber", "ter", "pe", "per"]
    suffixes = ["kan", "an", "i", "nya", "lah", "kah", "pun"]

    for prefix in prefixes:
        if word.startswith(prefix) and len(word) > len(prefix) + 2:
            word = word[len(prefix):]
            break

    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            word = word[: -len(suffix)]
            break

    return word
