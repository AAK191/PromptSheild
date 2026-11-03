import re
RULES = {
  (r"ignore (all |any )?(previous|prior|above) (instructions|prompts)", 0.9, "instruction_override"),
  (r"(reveal|show|print).{0,30}(system prompt|instructions)", 0.9, "prompt_leak"),
  (r"you are now|act as .{0,20}(dan|unrestricted)", 0.7, "jailbreak"),
  (r"developer mode|do anything now", 0.8, "jailbreak"),
  (r"disregard .{0,20}(rules|guidelines|safety)", 0.8, "instruction_override"),
  (r"(repeat|print|output|recite|copy|echo|display|write out|say).{0,30}(everything|all|text|words|content|messages?|instructions?).{0,20}(above|before|prior|preceding|earlier)", 0.8, "prompt_leak"),
(r"(verbatim|word for word).{0,40}(above|instructions|prompt|system|initial|first message)", 0.8, "prompt_leak"),
(r"(what|which).{0,20}(were|are|is).{0,20}(your|the) (initial|original|first|system|hidden )?(instructions|prompt|rules)", 0.8, "prompt_leak"),
(r"starting with .{0,3}you are", 0.8, "prompt_leak"),
(r"(forget|drop|abandon|discard) (all |any )?(your|the|previous|prior) (rules|instructions|guidelines|restrictions|programming)", 0.8, "instruction_override"),
(r"(what|which).{0,25}(text|message|words|content).{0,30}(before|preceding|prior to).{0,25}(my|the) (first|initial|opening)", 0.8, "prompt_leak"),
(r"(paste|print|show|give).{0,15}(me )?(it|that|the text|the message).{0,10}here", 0.5, "prompt_leak"),
}

COMPACT = [(re.compile(p.replace(" ", r"\s*")), w, c) for p, w, c in RULES]

def check_compact(text: str):
    squashed = re.sub(r"[^a-z0-9]", "", text)
    hits = [(c, w) for rx, w, c in COMPACT if rx.search(squashed)]
    return max((w for _, w in hits), default=0.0), [c for c, _ in hits]

def check(text: str):
    hits = [(cat, w) for p, w, cat in RULES if re.search(p, text)]
    score = max((w for _, w in hits), default=0.0)
    return score, [c for c, _ in hits]