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
  example  - a usage sentence for the curated Essentials set
  curated  - True for the 50 hand-written ESL essentials
  alts     - extra senses preserved when duplicate source entries are merged

Run this after changing the source markdown. It rewrites both idioms.json and the
embedded <script id="idiom-data"> block in index.html; the artwork payload and
all CSS/JS in the page are left untouched.
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
# Essentials: a curated ESL layer written for this site. The source book omits
# many very common idioms and provides no example sentences at all. Each entry
# below has a plain-English meaning plus a usage example. If the idiom already
# exists in the source we enrich that record rather than adding a duplicate
# card; otherwise we add a new record with an id >= 9000.
# Format: (term, meaning, example, primary topic, second topic, level)
# ---------------------------------------------------------------------------
CURATED = [
    ("A blessing in disguise", "something that seems unlucky at first but turns out to be good",
     "Missing the train was a blessing in disguise: I met an old friend on the next one.",
     "Success & Failure", "Feelings & Mood", 1),
    ("Add insult to injury", "to make a bad situation even worse",
     "I missed the bus, and to add insult to injury it started raining.",
     "Feelings & Mood", "Success & Failure", 1),
    ("Back to square one", "to have to start all over again because a plan failed",
     "The client rejected the design, so we are back to square one.",
     "Work & Business", "Success & Failure", 1),
    ("Better late than never", "it is better to do something late than not do it at all",
     "He finally apologised, but better late than never.",
     "Time & Speed", "Everyday Expressions", 1),
    ("Bite the bullet", "to force yourself to do something difficult or unpleasant",
     "I hate going to the dentist, but I just have to bite the bullet.",
     "Feelings & Mood", "Mind & Ideas", 2),
    ("Break the ice", "to say something friendly that helps people relax when they first meet",
     "Our teacher told a joke to break the ice on the first day of class.",
     "Talk & Truth", "Friends & Family", 1),
    ("Burn the midnight oil", "to work or study very late into the night",
     "She burned the midnight oil to finish her thesis before the deadline.",
     "Work & Business", "Time & Speed", 2),
    ("By the book", "exactly following the rules or official procedure",
     "The inspector does everything by the book, so do not expect any shortcuts.",
     "Work & Business", "People & Character", 2),
    ("Call it a day", "to stop working on something and finish for now",
     "We have planted enough trees; let's call it a day.",
     "Work & Business", "Time & Speed", 1),
    ("Cost an arm and a leg", "to be extremely expensive",
     "That laptop costs an arm and a leg, so I am waiting for a sale.",
     "Money & Value", "Everyday Expressions", 1),
    ("Cut corners", "to do something quickly and cheaply by skipping important steps",
     "Do not cut corners on the wiring just to save a little money.",
     "Work & Business", "Money & Value", 1),
    ("Cut to the chase", "to stop giving background details and say the main point",
     "Let me cut to the chase: we cannot afford this project.",
     "Talk & Truth", "Work & Business", 1),
    ("Down to earth", "practical, sensible and easy to talk to",
     "Despite being famous, she is completely down to earth.",
     "People & Character", "Feelings & Mood", 1),
    ("Face the music", "to accept criticism or punishment for something you did wrong",
     "He broke the window and then had to face the music.",
     "Feelings & Mood", "People & Character", 2),
    ("Get a taste of your own medicine", "to be treated the same bad way you have treated others",
     "You ignored my calls for weeks, so now you are getting a taste of your own medicine.",
     "People & Character", "Talk & Truth", 2),
    ("Get out of hand", "to become impossible to control",
     "The argument got out of hand and the teacher had to step in.",
     "Feelings & Mood", "Talk & Truth", 1),
    ("Get the hang of it", "to learn how to do something after some practice",
     "Driving on the left felt strange, but I got the hang of it after a week.",
     "Mind & Ideas", "Everyday Expressions", 1),
    ("Give someone the benefit of the doubt", "to believe someone is probably honest even when you are not sure",
     "I will give him the benefit of the doubt and assume the email got lost.",
     "People & Character", "Talk & Truth", 2),
    ("Go the extra mile", "to make more effort than is normally expected",
     "The nurse really went the extra mile to make my grandmother comfortable.",
     "Work & Business", "People & Character", 1),
    ("Hang in there", "to keep trying and not give up during a hard time",
     "I know the course is difficult, but hang in there - it gets easier.",
     "Feelings & Mood", "Success & Failure", 1),
    ("Hit the books", "to start studying hard",
     "I have an exam on Monday, so I need to hit the books this weekend.",
     "Mind & Ideas", "Work & Business", 1),
    ("Hit the nail on the head", "to describe a problem or situation exactly right",
     "You hit the nail on the head: the real issue is the deadline, not the budget.",
     "Talk & Truth", "Mind & Ideas", 1),
    ("Hit the sack", "to go to bed",
     "It is almost midnight; I am going to hit the sack.",
     "Health & Body", "Time & Speed", 1),
    ("In the nick of time", "just before it is too late",
     "We reached the station in the nick of time - the train left a minute later.",
     "Time & Speed", "Everyday Expressions", 1),
    ("Keep an eye on", "to watch someone or something carefully",
     "Could you keep an eye on the soup while I answer the door?",
     "Everyday Expressions", "Mind & Ideas", 1),
    ("Keep your chin up", "to stay cheerful when things are going badly",
     "Keep your chin up; you will find a new job soon.",
     "Feelings & Mood", "Friends & Family", 1),
    ("Kill two birds with one stone", "to solve two problems with a single action",
     "I killed two birds with one stone by visiting my parents and picking up the parcel on the same trip.",
     "Success & Failure", "Work & Business", 1),
    ("Let sleeping dogs lie", "to avoid bringing up an old problem that is now quiet",
     "The argument was settled months ago; let's let sleeping dogs lie.",
     "Talk & Truth", "Animals & Weather", 2),
    ("Let the cat out of the bag", "to reveal a secret, often by accident",
     "I let the cat out of the bag and told her about the surprise party.",
     "Talk & Truth", "Everyday Expressions", 1),
    ("Look on the bright side", "to think about the good part of a bad situation",
     "Look on the bright side: at least nobody was hurt.",
     "Feelings & Mood", "Mind & Ideas", 1),
    ("Miss the boat", "to miss a chance because you acted too slowly",
     "The tickets sold out yesterday, so I am afraid we missed the boat.",
     "Time & Speed", "Success & Failure", 1),
    ("Once in a blue moon", "very rarely",
     "I only eat fast food once in a blue moon.",
     "Time & Speed", "Everyday Expressions", 1),
    ("On the fence", "unable or unwilling to choose a side",
     "She is still on the fence about which university to attend.",
     "Mind & Ideas", "Success & Failure", 1),
    ("On the same page", "in agreement and sharing the same understanding",
     "Let's meet before the launch so everyone is on the same page.",
     "Talk & Truth", "Work & Business", 1),
    ("Out of the blue", "completely unexpectedly, without any warning",
     "Out of the blue, an old classmate called me after ten years.",
     "Time & Speed", "Feelings & Mood", 1),
    ("Piece of cake", "very easy to do",
     "The quiz was a piece of cake - I finished in five minutes.",
     "Success & Failure", "Everyday Expressions", 1),
    ("Pull someone's leg", "to tease someone by telling them something untrue as a joke",
     "Relax, I am just pulling your leg; there is no exam today.",
     "Talk & Truth", "Friends & Family", 1),
    ("Raining cats and dogs", "raining very heavily",
     "We stayed inside because it was raining cats and dogs.",
     "Animals & Weather", "Everyday Expressions", 1),
    ("See eye to eye", "to agree completely with someone",
     "My brother and I do not always see eye to eye on politics.",
     "Friends & Family", "Talk & Truth", 1),
    ("Speak of the devil", "said when the person you were just talking about appears",
     "Speak of the devil! We were just saying you should join us.",
     "Talk & Truth", "Everyday Expressions", 1),
    ("Spill the beans", "to tell a secret that should have been kept",
     "Come on, spill the beans - who is getting married?",
     "Talk & Truth", "Everyday Expressions", 1),
    ("Take it easy", "to relax and avoid stress",
     "You have been working all week; take it easy this weekend.",
     "Health & Body", "Feelings & Mood", 1),
    ("Take it with a grain of salt", "to not fully believe something because it may be exaggerated",
     "He always exaggerates, so take his story with a grain of salt.",
     "Mind & Ideas", "Talk & Truth", 2),
    ("The ball is in your court", "it is your turn to make the next decision or move",
     "I have sent you the offer, so the ball is in your court.",
     "Sports & Games", "Work & Business", 2),
    ("The last straw", "the final small problem that makes you lose patience",
     "The train was late again, and that was the last straw.",
     "Feelings & Mood", "Success & Failure", 1),
    ("The tip of the iceberg", "only a small visible part of a much bigger problem",
     "These three complaints are just the tip of the iceberg.",
     "Mind & Ideas", "Work & Business", 2),
    ("Through thick and thin", "in good times and bad times, staying loyal",
     "They have been friends through thick and thin for thirty years.",
     "Friends & Family", "People & Character", 2),
    ("Under the weather", "slightly ill or not feeling well",
     "I am feeling a bit under the weather, so I will stay home today.",
     "Health & Body", "Everyday Expressions", 1),
    ("Up in the air", "not yet decided or settled",
     "Our summer plans are still up in the air.",
     "Mind & Ideas", "Time & Speed", 1),
    ("Wrap your head around", "to manage to understand something complicated",
     "It took me a while to wrap my head around the new tax rules.",
     "Mind & Ideas", "Work & Business", 2),
]
assert len(CURATED) == 50, f"expected 50 essentials, got {len(CURATED)}"

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


def norm_key(term: str) -> str:
    """Case/punctuation-insensitive key for merging and curated matching."""
    t = term.lower().replace("\u2019", "'").replace("\u2018", "'")
    t = re.sub(r"[^a-z0-9' ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# --- Merge duplicate source entries -----------------------------------------
# The book lists several idioms twice with slightly different glosses. Keep one
# card and preserve the other senses in `alts` so nothing is lost.
source_count = len(records)
merged, seen = [], {}
for r in records:
    k = norm_key(r["term"])
    if k in seen:
        first = seen[k]
        other = r["def"].strip()
        if other and other.lower() != first["def"].lower():
            first.setdefault("alts", []).append(other)
        for t in r["cats"]:
            if t not in first["cats"]:
                first["cats"].append(t)
        continue
    seen[k] = r
    merged.append(r)
records = merged
merged_away = source_count - len(records)

# --- Curated Essentials ------------------------------------------------------
valid_topics = {name for name, _, _ in TOPICS} | {FALLBACK}
for term, _meaning, _example, c1, c2, _level in CURATED:
    assert c1 in valid_topics and (c2 is None or c2 in valid_topics), term

by_term = {norm_key(r["term"]): r for r in records}
new_records = []
next_id = 9000
for term, meaning, example, c1, c2, level in CURATED:
    cats = [c1] + ([c2] if c2 else [])
    r = by_term.get(norm_key(term))
    if r is None:
        next_id += 1
        ch = term[0].upper() if term else "#"
        r = {
            "id": next_id,
            "term": term,
            "def": meaning,
            "cat": c1,
            "cats": cats,
            "level": level,
            "letter": ch if "A" <= ch <= "Z" else "#",
            "words": len(re.findall(r"[A-Za-z0-9']+", term)),
            "note": "",
            "src": "essentials",
        }
        by_term[norm_key(term)] = r
        new_records.append(r)
    else:
        r["def"] = meaning
        r["cat"] = c1
        r["cats"] = cats
        r["level"] = level
    r["example"] = example
    r["curated"] = True
records.extend(new_records)

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
print("duplicate source entries merged away:", merged_away)
print("essentials:", sum(1 for r in records if r.get("curated")),
      "(", len(new_records), "new idioms, ",
      len(CURATED) - len(new_records), "existing ones enriched )")
print("records with an example:", sum(1 for r in records if r.get("example")))
print("records with alternate senses:", sum(1 for r in records if r.get("alts")))
