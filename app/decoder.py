import base64, binascii, html, math, re, unicodedata, urllib.parse
from collections import Counter

B64_RE = re.compile(r"[A-Za-z0-9+/_\-]{16,}={0,2}")
B32_RE = re.compile(r"[A-Za-z2-7]{16,}={0,6}")
HEX_RE = re.compile(r"(?:0x)?(?:[0-9a-fA-F]{2}[\s,]?){10,}")
BIN_RE = re.compile(r"(?:[01]{8}[\s,]?){6,}")
MAX_DEPTH, MAX_LAYERS = 3, 40

# ---------- Fix: non-English text ----------
def _looks_like_text(s: str) -> bool:
    """Unicode-aware: letters/marks/numbers/punct/space in ANY script count as text."""
    if len(s) < 8:
        return False
    ok = sum(unicodedata.category(c)[0] in "LMNPZ" or c in "\n\t" for c in s)
    lm = sum(unicodedata.category(c)[0] in "LM" for c in s)
    return ok / len(s) > 0.9 and lm / len(s) > 0.5

def _pad(t: str, n: int) -> str:
    return t + "=" * (-len(t) % n)

def _b64(tok):
    try:
        t = _pad(tok.replace("-", "+").replace("_", "/"), 4)
        s = base64.b64decode(t, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return None
    return s if _looks_like_text(s) else None

def _b32(tok):
    try:
        s = base64.b32decode(_pad(tok.upper(), 8)).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return None
    return s if _looks_like_text(s) else None

def _hex(tok):
    h = re.sub(r"0x|[\s,]", "", tok)
    try:
        s = bytes.fromhex(h).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None
    return s if _looks_like_text(s) else None

def _bin(tok):
    bits = re.sub(r"[\s,]", "", tok)
    try:
        s = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits) - len(bits) % 8, 8)).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None
    return s if _looks_like_text(s) else None

def _escapes(text):
    return re.sub(r"\\u([0-9a-fA-F]{4})|\\x([0-9a-fA-F]{2})",
                  lambda m: chr(int(m.group(1) or m.group(2), 16)), text)

# ---------- Layer 1: decoders (recursive) ----------
def _decoders(text):
    for tok in B64_RE.findall(text):
        if (d := _b64(tok)): yield "base64", d
    for tok in B32_RE.findall(text):
        if (d := _b32(tok)): yield "base32", d
    for tok in HEX_RE.findall(text):
        if (d := _hex(tok)): yield "hex", d
    for tok in BIN_RE.findall(text):
        if (d := _bin(tok)): yield "binary", d
    if "%" in text and (d := urllib.parse.unquote(text)) != text:
        yield "url", d
    if "&" in text and (d := html.unescape(text)) != text:
        yield "html", d
    if ("\\u" in text or "\\x" in text) and (d := _escapes(text)) != text:
        yield "escape", d

def expand(text: str):
    """Breadth-first decode. Returns [(path, text)], 'raw' first. Deduplicated and capped."""
    out, seen, frontier = [("raw", text)], {text}, [("raw", text)]
    for _ in range(MAX_DEPTH):
        nxt = []
        for path, t in frontier:
            for method, d in _decoders(t):
                if d in seen:
                    continue
                seen.add(d)
                nxt.append((method if path == "raw" else f"{path}>{method}", d))
        out += nxt
        frontier = nxt
        if len(out) >= MAX_LAYERS:
            break
    return out[:MAX_LAYERS]

# ---------- Layer 2: variants (applied once per text) ----------
COMMON = set("""the a an and or but if then of to in on for with at by from as is are was were be been
am i you he she it we they me my your our their this that these those not no do does did have has had
can could will would should ignore previous prior above instructions instruction reveal show system
prompt rules all any now act pretend tell what how why who please follow answer say print repeat
disregard forget guidelines safety developer mode""".split())

def english_score(t: str) -> float:
    words = re.findall(r"[a-z']+", t.lower())
    if len(words) < 3:
        return 0.0
    return sum(w in COMMON for w in words) / len(words)

def _shift(t, k):
    return "".join(chr((ord(c) - 97 + k) % 26 + 97) if "a" <= c <= "z" else c for c in t)

LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s",
                      "7": "t", "@": "a", "$": "s", "!": "i", "+": "t"})
CONCAT = re.compile(r"[\"'`]\s*[+,]?\s*[\"'`]")   # "ignore " + "previous"  ->  ignore previous

def variants(n: str):
    """n is already normalized (lowercase). Returns [(name, text)]."""
    out = []
    base = english_score(n)

    for k in range(1, 26):                         # k=13 is ROT13
        v = _shift(n, k)
        es = english_score(v)
        if es >= 0.2 and es > base + 0.15:         # must be clearly MORE readable than the input
            out.append((f"caesar{k}", v))

    for name, v in (("reversed", n[::-1]),
                    ("word_reversed", " ".join(w[::-1] for w in n.split()))):
        es = english_score(v)
        if es >= 0.2 and es > base + 0.15:
            out.append((name, v))

    if (v := n.translate(LEET)) != n:
        out.append(("leet", v))
    if (v := CONCAT.sub("", n)) != n:
        out.append(("concat", v))
    return out


# ---------- Layer 3: "I can't decode it, but it smells like an attack" ----------
INTENT = re.compile(r"\b(decode|decrypt|decipher|deobfuscate|base ?64|rot ?13|"
                    r"follow (it|them|the (decoded|hidden))|obey|execute (it|the))\b")
BLOB_RE = re.compile(r"[A-Za-z0-9+/=_\-]{24,}")

def _entropy(s):
    c, n = Counter(s), len(s)
    return -sum(v / n * math.log2(v / n) for v in c.values())

def unknown_encoding_score(raw: str):
    if not INTENT.search(raw.lower()):
        return 0.0, []
    for tok in BLOB_RE.findall(raw):
        if _entropy(tok) >= 4.1 and _b64(tok) is None and _b32(tok) is None:
            return 0.5, ["unknown_encoding"]   # gray zone, not an outright block
    return 0.0, []