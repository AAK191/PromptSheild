import re

CANARY = "PSCANARY-7f3a9c"   # secret marker planted in the system prompt

SECRET_PATTERNS = {
    "openai_key":     r"sk-[A-Za-z0-9_\-]{20,}",
    "aws_key":        r"AKIA[0-9A-Z]{16}",
    "github_token":   r"ghp_[A-Za-z0-9]{36}",
    "private_key":    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "generic_secret": r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*\S{8,}",
}

PII_PATTERNS = {
    "email":       r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
    "phone_in":    r"(?<!\d)(?:\+91[\s\-]?)?[6-9]\d{9}(?!\d)",
    "aadhaar":     r"(?<!\d)\d{4}\s?\d{4}\s?\d{4}(?!\d)",
    "credit_card": r"(?<!\d)(?:\d[ \-]?){13,16}(?!\d)",
}

def _words(text: str):
    return re.findall(r"[a-z0-9']+", text.lower())

def _ngram_overlap(system_prompt: str, reply: str, n: int = 5) -> float:
    """Fraction of the system prompt's word n-grams that appear in the reply."""
    sw, rw = _words(system_prompt), _words(reply)
    if len(sw) < n:
        return 0.0
    sys_grams = {tuple(sw[i:i + n]) for i in range(len(sw) - n + 1)}
    rep_grams = {tuple(rw[i:i + n]) for i in range(len(rw) - n + 1)}
    return len(sys_grams & rep_grams) / len(sys_grams)

def shield_output(reply: str, system_prompt: str) -> dict:
    findings, blocked, cleaned = [], False, reply

    # 1. System prompt leakage
    if CANARY.lower() in reply.lower():
        findings.append("canary_leak"); blocked = True
    overlap = _ngram_overlap(system_prompt, reply)
    if overlap >= 0.3:
        findings.append(f"system_prompt_overlap:{overlap:.2f}"); blocked = True

    # 2. Secrets
    for name, pat in SECRET_PATTERNS.items():
        if re.search(pat, reply):
            findings.append(f"secret:{name}"); blocked = True

    # 3. PII (redact, don't block)
    for name, pat in PII_PATTERNS.items():
        if re.search(pat, cleaned):
            findings.append(f"pii:{name}")
            cleaned = re.sub(pat, f"[REDACTED_{name.upper()}]", cleaned)

    return {"blocked": blocked, "findings": findings, "response": cleaned}