import re, unicodedata

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    HOMOGLYPHS = str.maketrans("аеорсхуіѕοινρ", "aeopcxyisoivp")
    text = text.translate(HOMOGLYPHS)
    text = re.sub(r"[\u200b-\u200f\u202a-\u202e]", "", text)
    return re.sub(r"\s+", " ", text).strip()