#!/usr/bin/env python3
"""Build idioms.json from 'Min isms.md' (American Idiomology, HOF Publications 2019).

Source format:   N. **idiom** (definition)
A few dozen entries have broken parentheses, truncated text, or no definition at
all. This parser handles those cases, then enriches every entry with:
  letter   - A-Z bucket ('#' for numbers / symbols)
  cat      - a topic tag inferred from the definition (the book's own 20-part
             taxonomy exists but is empty, so topics are derived instead)
  level    - 1/2/3 estimated difficulty, from phrase length, word rarity,
             definition complexity and culture-specific references
  words    - phrase length, for sorting
  note     - 'editor' where a definition was supplied/completed by the editor
"""
import json
import re
from pathlib import Path

SRC = Path("/Users/pinghao/Downloads/Min isms.md")
OUT = Path(__file__).with_name("idioms.json")

raw_lines = SRC.read_text(encoding="utf-8").split("\n")

# Section 1 (the numbered list) sits between these two markers.
start = next(i for i, l in enumerate(raw_lines) if l.strip().startswith("1. **0 tolerance**"))
end = next(i for i, l in enumerate(raw_lines) if l.strip().startswith("3002. **Zoned out**"))
lines = raw_lines[start:end + 1]


def unescape(s: str) -> str:
    # Markdown escaped punctuation: \-  \$  \!  \#  \)  \`
    return re.sub(r"\\([^\w\s])", r"\1", s)


def clean(s: str) -> str:
    s = unescape(s).strip()
    s = re.sub(r"^\(+", "", s)
    s = re.sub(r"[\s\)]+$", "", s)
    s = re.sub(r"[\s\.\"”'’]+$", "", s)
    return s.strip()


def parse(line: str):
    m = re.match(r"^(\d+)\.\s+(.*)$", line.strip())
    if not m:
        return None
    num = int(m.group(1))
    body = unescape(m.group(2)).strip()
    if "**" not in body:            # stray fragment (#2297) with no bolded idiom
        return None
    parts = body.split("**")
    term = parts[1].strip() if len(parts) > 2 else body.replace("**", "").strip()
    tail = "**".join(parts[2:]).strip() if len(parts) > 2 else ""

    # Bold marker landed inside the opening paren: **Fire sale (**Everything ...
    if term.endswith("("):
        return num, term[:-1].strip(), clean(tail)

    # Words after the bold marker but before '(' belong to the idiom: **Fault** finder (...)
    if tail and not tail.startswith("(") and "(" in tail:
        prefix, _, rest = tail.partition("(")
        term = (term + " " + prefix.strip()).strip()
        tail = "(" + rest

    if tail.startswith("("):
        definition = clean(tail)
    elif "(" in term and term.endswith(")"):   # **Crowded field (many competitors)**
        term, _, rest = term.rpartition("(")
        definition = clean(rest)
        term = term.strip()
    else:
        definition = ""
    return num, term, definition


entries = []
for line in lines:
    parsed = parse(line)
    if parsed:
        entries.append(parsed)

# ---------------------------------------------------------------------------
# Definitions that are missing or cut off in the source. Marked 'editor' so the
# site can be transparent about them.
# ---------------------------------------------------------------------------
EDITOR_DEFS = {
    891:  "following others blindly, without thinking for oneself",
    1111: "everyone involved working together through the small details until they agree",
    1150: "not yet noticed, or not yet important enough to deal with",
    1312: "a very strong, loud wind",
    1761: "to call in someone who can stop a crisis or put out a growing problem",
    1836: "feeling isolated and alone, with no one to rely on",
    2071: "a fast-moving river, either a mountain river or one swollen with water",
    2380: "extremely hot weather",
    2390: "a hidden plan, trick or advantage kept ready to use",
    2585: "suffering setbacks but still carrying on and functioning",
}

# ---------------------------------------------------------------------------
# Topic classification. Each topic has distinctive (weight 3) and supporting
# (weight 1) cues. Scored on the definition, with a smaller bonus for cues in
# the idiom itself.
# ---------------------------------------------------------------------------
TOPICS = [
    ("Feelings & Mood", [
        "happy", "sad", "angry", "mad", "upset", "depressed", "worried", "nervous",
        "afraid", "scared", "excited", "joy", "bored", "embarrassed", "ashamed",
        "proud", "frustrated", "anxious", "mood", "emotion", "grief", "sorrow",
    ], ["feeling", "feel", "cry", "crying", "laugh", "smile", "temper", "fear",
        "shame", "humiliation", "cheer", "gloom", "pouting", "disappointed",
        "euphoria", "unhappy", "annoyed", "irritated", "shock", "surprise"]),
    ("People & Character", [
        "personality", "trustworthy", "honest", "humble", "arrogant", "egotistical",
        "selfish", "generous", "stubborn", "lazy", "coward", "surly", "reputation",
        "character", "integrity", "liar", "saint", "villain", "snob",
    ], ["person", "someone", "one's character", "kind", "mean", "rude", "polite",
        "clever", "foolish", "stupid", "idiot", "intelligent", "smart", "wise",
        "dumb", "brave", "talented", "attitude", "behavior"]),
    ("Work & Business", [
        "job", "project", "employee", "employer", "boss", "career", "deadline",
        "workplace", "manager", "promotion", "fired", "hired", "company", "office",
        "assignment", "business", "client", "customer", "workload",
    ], ["work", "working", "task", "meeting", "staff", "team", "product", "sales",
        "organization", "proposal", "hire", "supervisor", "shift", "duties"]),
    ("Money & Value", [
        "money", "dollar", "cash", "salary", "expensive", "wealthy", "rich", "poor",
        "debt", "budget", "investment", "profit", "financial", "paycheck", "broke",
        "cost", "price", "purchase", "wager",
    ], ["pay", "paid", "spend", "spending", "save", "worth", "value", "buy",
        "sell", "bill", "bet", "free", "cheap", "loss", "economic"]),
    ("Success & Failure", [
        "victory", "defeat", "succeed", "success", "failure", "champion", "achieve",
        "accomplish", "outcome", "competition", "advantage", "underdog",
    ], ["win", "won", "lose", "lost", "fail", "failed", "attempt", "effort",
        "result", "beat", "compete", "score", "chance", "luck", "best", "worst",
        "goal", "finish", "performance"]),
    ("Time & Speed", [
        "quickly", "immediately", "eventually", "suddenly", "deadline", "hurried",
        "delay", "hurry", "instant", "minute", "hour", "forever", "procrastinate",
    ], ["quick", "fast", "slow", "late", "early", "soon", "time", "moment",
        "wait", "waiting", "short", "long", "day", "night", "future", "past",
        "now", "temporary", "finally", "before", "after"]),
    ("Health & Body", [
        "sick", "exhausted", "hospital", "doctor", "medicine", "hangover", "injury",
        "drunk", "pain", "sore", "headache", "illness", "death", "die", "dead",
    ], ["health", "tired", "sleep", "asleep", "energy", "hurt", "body", "head",
        "face", "hand", "foot", "feet", "eye", "eyes", "nose", "mouth", "hair",
        "leg", "legs", "blood", "heart", "sweat", "rest", "worn out"]),
    ("Talk & Truth", [
        "conversation", "rumor", "gossip", "promise", "statement", "reprimand",
        "silence", "exaggeration", "secret", "confession", "argument",
    ], ["say", "said", "speak", "talk", "told", "tell", "discuss", "word",
        "words", "story", "lie", "lying", "truth", "listen", "hear", "heard",
        "ask", "answer", "reply", "joke", "explain", "announce", "quiet", "shut up"]),
    ("Friends & Family", [
        "friend", "friends", "family", "wife", "husband", "married", "dating",
        "neighbor", "relationship", "couple", "mother", "father", "parent",
        "brother", "sister", "wedding",
    ], ["love", "child", "children", "kid", "kids", "guest", "crowd", "group",
        "party", "together", "alone", "help", "support", "social", "date"]),
    ("Food & Drink", [
        "coffee", "beer", "whiskey", "alcohol", "kitchen", "restaurant", "hungry",
        "thirst", "breakfast", "lunch", "dinner", "pancake", "sandwich", "cake",
    ], ["food", "eat", "eating", "drink", "drinking", "cook", "egg", "eggs",
        "bread", "soup", "milk", "meal", "cup", "taste", "sweet", "sour",
        "pot", "pan", "snack", "bite"]),
    ("Sports & Games", [
        "baseball", "football", "golf", "basketball", "poker", "inning", "touchdown",
        "home run", "boxing", "championship", "referee", "horse race", "deck of cards",
    ], ["game", "ball", "card", "cards", "race", "racing", "player", "coach",
        "score", "pitch", "strike", "punch", "fishing", "hunting", "bet",
        "team", "hole", "shot"]),
    ("Animals & Weather", [
        "dog", "cat", "horse", "bird", "fish", "cow", "pig", "chicken", "duck",
        "mule", "monkey", "bear", "wolf", "sheep", "lamb", "goose", "lemming",
        "rain", "snow", "storm", "sunshine", "weather", "river", "ocean",
    ], ["animal", "wind", "sun", "cloud", "hot", "cold", "fire", "water",
        "sea", "mountain", "tree", "bug", "insect", "rat", "mouse"]),
    ("Places & Travel", [
        "city", "town", "street", "highway", "airplane", "travel", "nickname for",
        "name for", "neighborhood", "bridge", "highway",
    ], ["place", "road", "car", "drive", "driving", "train", "plane", "trip",
        "house", "home", "door", "wall", "room", "bar", "club", "school",
        "church", "farm", "map", "direction", "corner", "block", "park"]),
    ("Mind & Ideas", [
        "understand", "remember", "forget", "decision", "imagine", "intelligence",
        "memory", "confused", "realize", "knowledge", "sanity", "crazy",
    ], ["think", "thought", "know", "knew", "idea", "learn", "plan", "guess",
        "believe", "mind", "brain", "attention", "smart", "sense", "reason",
        "consider", "aware", "logic", "foolish"]),
]

import math

# Cue weights are data-driven: a word that appears in many definitions (e.g.
# "person") is a weak signal; a rare one (e.g. "baseball") is a strong signal.
_corpus = [(t + " " + d).lower() for _, t, d in
           [(n, t, EDITOR_DEFS.get(n, d)) for n, t, d in entries]]
_all_cues = sorted({k for _, strong, weak in TOPICS for k in strong + weak})
_df = {k: sum(1 for text in _corpus
              if re.search(r"\b" + re.escape(k) + r"\b", text)) for k in _all_cues}
_w = {k: min(3.5, max(0.4, round(math.log(len(_corpus) / max(1, _df[k])) * 0.72, 2)))
      for k in _all_cues}
CUE_CACHE = [(name, [(re.compile(r"\b" + re.escape(k) + r"\b", re.I), _w[k])
                     for k in strong + weak]) for name, strong, weak in TOPICS]

FALLBACK = "Everyday Expressions"


def classify(term: str, definition: str):
    """Return (primary tag, list of up to two tags)."""
    text = definition or term
    scored = []
    for name, cues in CUE_CACHE:
        score = sum(w for pat, w in cues if pat.search(text))
        score += sum(w * 0.6 for pat, w in cues if w >= 2.0 and pat.search(term))
        if score >= 1.5:
            scored.append((score, name))
    scored.sort(reverse=True)
    if not scored:
        return FALLBACK, [FALLBACK]
    tags = [scored[0][1]]
    if len(scored) > 1 and scored[1][0] >= max(1.5, scored[0][0] * 0.55):
        tags.append(scored[1][1])
    return tags[0], tags


# ---------------------------------------------------------------------------
# Difficulty: phrase length, share of uncommon words, definition complexity and
# culture-specific references. Thresholds are percentile-based so the three
# levels stay useful as filters.
# ---------------------------------------------------------------------------
COMMON = set("""a an the and or but if then than so to of in on at by for with from
about into over under after before up down out off again once here there when
where why how what which who whom whose this that these those i you he she it we
they me him her us them my your his its our their mine yours ours theirs myself
yourself himself herself itself ourselves themselves is am are was were be been
being do does did done have has had having will would can could shall should may
might must not no nor yes just very too also only even still yet ever never
always often sometimes all any some none one two three four five six seven eight
nine ten first second third last next other another each every both few many much
more most less least own same such get got go goes going went come came take took
taken make made made put said say says see saw seen know knew think thought want
give gave use used find found tell feel keep let begin seem help show hear play
run move like live believe bring happen write provide sit stand lose pay meet
include continue set learn change lead understand watch follow stop create speak
read allow add spend grow open walk win offer remember love consider appear buy
wait serve die send expect build stay fall cut reach kill remain don't doesn't
didn't can't couldn't won't wouldn't isn't aren't wasn't weren't i'm it's that's
there's he's she's you're we're they're let's one's you'll i'll he'll she'll
we'll they'll ain't thing things stuff way ways person people time times day days
good bad big small little long short new old right wrong real great well better
best high low hard easy full half whole lot bit part place side end back front
top bottom head hand eye foot face word world life man men woman women boy girl
child kid home house room door water fire air money job work game ball line point
""".split())

CULTURE = re.compile(
    r"\b(baseball|football|golf|poker|basketball|inning|touchdown|home run|"
    r"deck of cards|bible|biblical|general|congress|president|senator|"
    r"american indian|mt\. rushmore|brooks|yankees|super bowl|world series|"
    r"u\.?s\.? currency|philadelphia|detroit|chicago|hollywood|wall street|"
    r"union|war|colonial|shakespeare|einstein|cupid|blarney|mardi gras|"
    r"county|state fair|shot glass|whiskey|bourbon)\b", re.I)


def diff_score(term: str, definition: str) -> float:
    words = re.findall(r"[A-Za-z']+", term.lower())
    rare = [w for w in words if w not in COMMON and len(w) > 2]
    def_words = len(definition.split())
    score = 10 + min(26, max(0, len(words) - 1) * 5.5)
    score += min(30, len(rare) * 7)
    score += min(18, def_words / 4)
    if CULTURE.search(definition + " " + term):
        score += 9
    return score


records = []
for num, term, definition in entries:
    note = ""
    if num in EDITOR_DEFS:
        definition = EDITOR_DEFS[num]
        note = "editor"
    ch = term[0].upper() if term else "#"
    letter = ch if "A" <= ch <= "Z" else "#"
    primary, tags = classify(term, definition)
    records.append({
        "id": num,
        "term": term,
        "def": definition,
        "cat": primary,
        "cats": tags,
        "level": 1,
        "letter": letter,
        "words": len(re.findall(r"[A-Za-z0-9']+", term)),
        "score": round(diff_score(term, definition), 1),
        "note": note,
    })

scores = sorted(r["score"] for r in records)
low = scores[int(len(scores) * 0.36)]
high = scores[int(len(scores) * 0.74)]
for r in records:
    r["level"] = 1 if r["score"] < low else (2 if r["score"] < high else 3)
    del r["score"]

payload = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
OUT.write_text(payload, encoding="utf-8")

# Keep the self-contained website in sync with the data file.
SITE = Path(__file__).with_name("index.html")
if SITE.exists():
    safe = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    html, count = re.subn(
        r'(<script id="idiom-data" type="application/json">).*?(</script>)',
        lambda m: m.group(1) + safe + m.group(2),
        SITE.read_text(encoding="utf-8"), count=1, flags=re.S)
    if count:
        SITE.write_text(html, encoding="utf-8")
        print(f"updated embedded data in {SITE.name}")

from collections import Counter
print(f"wrote {len(records)} idioms -> {OUT} ({OUT.stat().st_size // 1024} KB)")
print("levels:", dict(Counter(r["level"] for r in records)))
print("topics (primary / any tag):")
primary_counts = Counter(r["cat"] for r in records)
tag_counts = Counter(t for r in records for t in r["cats"])
for k, v in primary_counts.most_common():
    print(f"  {k:<24} {v:>5} / {tag_counts[k]}")
print("letters:", dict(sorted(Counter(r["letter"] for r in records).items())))
print("editor-completed:", sum(1 for r in records if r["note"]))
