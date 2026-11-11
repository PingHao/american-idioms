#!/usr/bin/env python3
"""Apply the illustrated editorial redesign to index.html.

Run once from a pristine index.html. Artwork is read from art/web/*.webp and
embedded as data URIs so the site remains a single self-contained file.
"""
from pathlib import Path
import base64
import json

ROOT = Path(__file__).with_name("index.html")
ART_DIR = Path(__file__).with_name("art") / "web"

html = ROOT.read_text(encoding="utf-8")
if 'id="illustrated"' in html:
    raise SystemExit("Already applied. Restore index.html from /tmp/idiom-atlas-base.html first, "
                    "then run build_data.py followed by apply_fixes.py for the current build.")

art = {}
for p in sorted(ART_DIR.glob("*.webp")):
    art[p.stem] = "data:image/webp;base64," + base64.b64encode(p.read_bytes()).decode("ascii")
if len(art) != 8:
    raise SystemExit(f"Expected 8 web assets, found {len(art)}")

CSS = r'''
/* ============ Idiom Atlas · illustrated edition ============ */
:root{
  --bg:#111C31; --bg2:#16233C; --surface:#1B2A45; --surface2:#23344F;
  --border:#2E4261; --border2:#3D5578;
  --text:#F7F1E5; --muted:#AEBBD0; --faint:#7F8FA8;
  --accent:#F2A65A; --accent-soft:rgba(242,166,90,.15); --accent-ink:#241708;
  --l1:#5BD3A8; --l2:#F2C25C; --l3:#F58A7E;
  --shadow:0 18px 44px rgba(0,0,0,.42);
  --paper:#FBF6EA; --paper-line:#E7DCC7; --ink:#1D2A44; --ink2:#4C5872;
}
html[data-theme="light"]{
  --bg:#FBF6EA; --bg2:#F5EEDF; --surface:#FFFDF8; --surface2:#F7F0E2;
  --border:#E7DCC7; --border2:#D6C7AC;
  --text:#1D2A44; --muted:#69738D; --faint:#98A0B4;
  --accent:#DC5C36; --accent-soft:rgba(220,92,54,.10); --accent-ink:#fff;
  --l1:#1E9C7A; --l2:#C58412; --l3:#D2514A;
  --shadow:0 14px 34px rgba(62,48,26,.13);
}
body{background:var(--bg)}
.topbar{border-bottom:1px solid var(--border);background:color-mix(in srgb,var(--bg) 91%,transparent)}
.brand-mark{width:40px;height:40px;border-radius:13px;background:var(--accent);color:var(--accent-ink);padding:0}
.brand-mark svg{width:23px;height:23px;stroke-width:1.9}
.brand-text strong{font:400 19px/1.1 Georgia,"Times New Roman",serif;letter-spacing:-.01em}
.brand-text small{font-size:10.5px}
#q{background:var(--surface2);border-radius:12px}
.search-wrap kbd{font-size:10.5px}

/* ---- quick nav pills (borrowed from Word Atlas tabs) ---- */
.subbar{border-bottom:1px solid var(--border);background:var(--bg2)}
.subbar-inner{display:flex;align-items:center;gap:8px;height:50px;overflow-x:auto;scrollbar-width:none}
.subbar-inner::-webkit-scrollbar{display:none}
.quicknav{display:flex;gap:6px;flex:none}
.quicknav button{display:inline-flex;align-items:center;gap:7px;height:32px;padding:0 13px;border-radius:20px;border:1px solid var(--border);background:var(--surface);color:var(--muted);font-size:12.5px;font-weight:650;white-space:nowrap;transition:.15s}
.quicknav button:hover{color:var(--text);border-color:var(--border2);transform:translateY(-1px)}
.quicknav button svg{width:15px;height:15px}
.quicknav button.primary{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.subbar-note{margin-left:auto;font-size:11.5px;color:var(--faint);white-space:nowrap;flex:none}

/* ---- hero poster ---- */
.hero{border-bottom:0;background:transparent;padding:26px 0 0;overflow:hidden}
.hero-poster{position:relative;min-height:372px;border:1px solid var(--paper-line);border-radius:26px;overflow:hidden;background-color:var(--paper);background-image:linear-gradient(90deg,rgba(251,246,234,.98) 0%,rgba(251,246,234,.97) 38%,rgba(251,246,234,.78) 55%,rgba(251,246,234,0) 74%),var(--img-hero);background-size:cover;background-position:center right;padding:44px 46px;display:flex;align-items:center;color:var(--ink);box-shadow:var(--shadow)}
.hero-copy{max-width:47%}
.hero .eyebrow{color:#B8552D;font-size:10.5px}
.hero h1{color:var(--ink);font-size:clamp(30px,3.6vw,46px);line-height:1.12}
.hero h1 em{color:#D05B33}
.hero .lede{color:var(--ink2);font-size:14px;max-width:430px}
.hero-cta{display:flex;gap:9px;flex-wrap:wrap;margin-top:20px}
.hero-poster .btn,.banner-copy .btn{background:rgba(255,255,255,.78);border-color:rgba(29,42,68,.20);color:var(--ink)}
.hero-poster .btn:hover,.banner-copy .btn:hover{border-color:var(--accent)}
.hero-poster .btn.accent,.banner-copy .btn.accent{background:#DC5C36;border-color:#DC5C36;color:#fff}
.hero-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr)) minmax(0,1.7fr);gap:10px;margin:14px 0 0}
.hero-stats .stat{min-width:0;background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:12px 16px}
.hero-stats .stat b{font:400 24px/1.1 Georgia,serif}
.hero-stats .starmap{display:flex;flex-direction:row;align-items:center;justify-content:space-between;gap:10px;background:var(--accent-soft);border-color:color-mix(in srgb,var(--accent) 28%,transparent)}
.starmap-svg{flex:1;min-width:0}
.starmap-svg svg{width:100%;height:34px;display:block}
.hero-stats .starmap span{font-size:11px;color:var(--muted);white-space:nowrap;margin:0}

/* ---- illustrated section banners ---- */
.today-section,.topics-section,.study-cta{padding:34px 0 0}
.banner{display:grid;grid-template-columns:44% minmax(0,1fr);border:1px solid var(--paper-line);border-radius:22px;overflow:hidden;background:var(--paper);color:var(--ink);box-shadow:var(--shadow);min-height:210px}
.banner-art{position:relative;overflow:hidden;background:var(--paper)}
.banner-art img{display:block;width:100%;height:100%;object-fit:cover;object-position:center}
.banner-copy{padding:28px 32px;display:flex;flex-direction:column;justify-content:center;gap:8px}
.banner-kicker{margin:0;font:700 10px/1 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase;color:#B8552D}
.banner-copy h2{font:400 clamp(22px,2.4vw,30px)/1.2 Georgia,serif;letter-spacing:-.02em;margin:0;color:var(--ink)}
.banner-copy p{font-size:13px;line-height:1.6;color:var(--ink2);margin:0;max-width:430px}
.today-section .banner{margin-bottom:16px}
.section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:18px;margin:0 0 16px}
.section-head h2{font:400 clamp(24px,2.8vw,33px)/1.2 Georgia,serif;letter-spacing:-.02em;margin:0}
.section-head p{margin:5px 0 0;font-size:12.5px;color:var(--muted)}

/* ---- category tiles ---- */
.topic-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(174px,1fr));gap:12px}
.topic-tile{display:flex;flex-direction:column;text-align:left;padding:0 0 12px;border:1px solid var(--border);border-radius:16px;background:var(--surface);overflow:hidden;transition:.18s ease;cursor:pointer}
.topic-tile:hover{transform:translateY(-3px);border-color:var(--accent);box-shadow:var(--shadow)}
.topic-tile.active{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent-soft)}
.tile-art{position:relative;display:block;aspect-ratio:1.55/1;overflow:hidden;background:var(--paper)}
.tile-art img{width:100%;height:100%;object-fit:cover;object-position:center;display:block}
.tile-art::after{content:"";position:absolute;inset:0;background:var(--tile-tint,#DC5C36);mix-blend-mode:multiply;opacity:.15;pointer-events:none}
.tile-icon{position:absolute;left:10px;bottom:10px;z-index:2;width:30px;height:30px;border-radius:9px;display:grid;place-items:center;background:var(--tile-tint,#DC5C36);color:#fff;border:2px solid rgba(255,255,255,.85)}
.tile-icon svg{width:17px;height:17px;stroke-width:2}
.tile-name{font-size:13px;font-weight:700;padding:11px 12px 0;color:var(--text);line-height:1.3}
.tile-count{font-size:11px;color:var(--faint);padding:2px 12px 0}

/* ---- category icon badge on result cards (icon, not a per-entry image) ---- */
.cat-badge{width:26px;height:26px;border-radius:8px;display:grid;place-items:center;background:var(--surface2);border:1px solid var(--border);color:var(--accent)}
.cat-badge svg{width:15px;height:15px;stroke-width:1.9}
.card{border-radius:16px}
.card .term{font:400 18px/1.3 Georgia,serif}
.grid{gap:14px}
.chip,.tabs button.active,.filter-pill,.level{border-radius:20px}
.letters button{border-radius:9px}
.btn{border-radius:11px}
.study-cta{padding-bottom:6px}
.explore{padding-top:30px}

@media (max-width:980px){
  .hero-copy{max-width:64%}
  .hero-poster{min-height:330px;padding:34px}
  .hero-stats{grid-template-columns:repeat(4,minmax(0,1fr))}
  .banner{grid-template-columns:40% minmax(0,1fr)}
  .topic-grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}
}
@media (max-width:720px){
  .hero{padding-top:16px}
  .hero-poster{min-height:340px;padding:26px 22px;background-image:linear-gradient(180deg,rgba(251,246,234,.97) 0%,rgba(251,246,234,.94) 52%,rgba(251,246,234,.18) 100%),var(--img-hero);background-position:center bottom}
  .hero-copy{max-width:100%}
  .hero h1{font-size:30px}
  .hero-stats{grid-template-columns:repeat(2,minmax(0,1fr))}
  .hero-stats .starmap{grid-column:1/-1}
  .banner{grid-template-columns:minmax(0,1fr);min-height:0}
  .banner-art{aspect-ratio:2.1/1}
  .banner-copy{padding:22px}
  .topic-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
  .tile-name{font-size:12px}
  .subbar-inner{height:46px}
  .quicknav button{padding:0 10px;font-size:11.5px;gap:5px}
  .quicknav button svg{width:13px;height:13px}
  .subbar-note{display:none}
}
'''

JS_MAPS = r'''
/* ---------- illustrated edition: artwork, topic families, icons ---------- */
const ART = JSON.parse(document.getElementById("art-data").textContent);
document.documentElement.style.setProperty("--img-hero","url("+ART.hero+")");

const TOPIC_FAMILY = {
  "Time & Speed":"cat-ideas", "Mind & Ideas":"cat-ideas", "Success & Failure":"cat-ideas",
  "Work & Business":"cat-work", "Money & Value":"cat-work",
  "Talk & Truth":"cat-people", "Friends & Family":"cat-people", "People & Character":"cat-people", "Feelings & Mood":"cat-people",
  "Health & Body":"cat-nature", "Animals & Weather":"cat-nature", "Food & Drink":"cat-nature",
  "Places & Travel":"cat-places", "Everyday Expressions":"cat-places", "Sports & Games":"cat-places"
};
const TILE_TINT = {
  "Everyday Expressions":"#E0A23B", "Time & Speed":"#D98324", "Success & Failure":"#C9A227",
  "Work & Business":"#2F7FA8", "Money & Value":"#3E9B76", "Talk & Truth":"#D2603C",
  "Mind & Ideas":"#7A68B8", "Health & Body":"#D05A72", "Feelings & Mood":"#E07A9B",
  "Places & Travel":"#2E8C9E", "Friends & Family":"#C97B3C", "People & Character":"#5A7FB5",
  "Animals & Weather":"#4E9D8C", "Food & Drink":"#C25B3A", "Sports & Games":"#3F8F5B"
};
const sv = p => '<svg viewBox="0 0 24 24">'+p+'</svg>';
const TOPIC_ICON = {
  "Everyday Expressions": sv('<circle cx="12" cy="12" r="9"/><path d="M8 12h.01M12 12h.01M16 12h.01"/>'),
  "Time & Speed": sv('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
  "Success & Failure": sv('<path d="M7 4h10v5a5 5 0 01-10 0V4z"/><path d="M7 6H4v2a3 3 0 003 3M17 6h3v2a3 3 0 01-3 3M12 14v3M9 20h6"/>'),
  "Work & Business": sv('<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 012-2h4a2 2 0 012 2v2M3 12h18"/>'),
  "Talk & Truth": sv('<path d="M4 5h12a2 2 0 012 2v6a2 2 0 01-2 2H9l-5 3v-3a2 2 0 01-2-2V7a2 2 0 012-2z"/><path d="M20 9v6a2 2 0 01-2 2"/>'),
  "Mind & Ideas": sv('<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 00-3.5 10.9c.6.5.9 1.1 1 2.1h5c.1-1 .4-1.6 1-2.1A6 6 0 0012 3z"/>'),
  "Health & Body": sv('<path d="M12 20s-7-4.6-7-9.5A4 4 0 0112 8a4 4 0 017 2.5C19 15.4 12 20 12 20z"/>'),
  "Feelings & Mood": sv('<circle cx="12" cy="12" r="9"/><path d="M8 14c1 1.5 2.4 2.2 4 2.2s3-.7 4-2.2M9 9h.01M15 9h.01"/>'),
  "Places & Travel": sv('<path d="M12 21s-7-6-7-11a7 7 0 1114 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>'),
  "Friends & Family": sv('<circle cx="9" cy="8" r="3"/><path d="M3 20v-1a5 5 0 0110 0v1"/><circle cx="17" cy="9" r="2.5"/><path d="M15 20v-1a4 4 0 016-3.5"/>'),
  "Money & Value": sv('<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v5c0 1.7 3.1 3 7 3s7-1.3 7-3V6M5 11v5c0 1.7 3.1 3 7 3s7-1.3 7-3v-5"/>'),
  "People & Character": sv('<circle cx="12" cy="8" r="3.5"/><path d="M5 21v-2a7 7 0 0114 0v2"/>'),
  "Animals & Weather": sv('<path d="M7 18h10a4 4 0 000-8 6 6 0 00-11.6 1.5A3.5 3.5 0 007 18z"/><path d="M17 3v2M15.5 4.5l-1 1M20 6h-2"/>'),
  "Food & Drink": sv('<path d="M12 8c-2-2-6-1-6 3v7a3 3 0 003 3h6a3 3 0 003-3v-7c0-4-4-5-6-3z"/><path d="M12 8V5M12 5c1-2 3-2 4-1"/>'),
  "Sports & Games": sv('<circle cx="12" cy="12" r="9"/><path d="M12 3l3 4-1 5H10L9 7l3-4zM9 12l-6 3M15 12l6 3M10 17l2 4 2-4"/>')
};
function renderTopicTiles(){
  const order = TOPICS.slice().sort((a,b)=>TOPIC_COUNT[b]-TOPIC_COUNT[a]);
  $("#topicTiles").innerHTML = order.map(t =>
    '<button class="topic-tile" data-topic="'+esc(t)+'" style="--tile-tint:'+(TILE_TINT[t]||"#DC5C36")+'">'
    + '<span class="tile-art"><img loading="lazy" src="'+ART[TOPIC_FAMILY[t]||"cat-places"]+'" alt="" aria-hidden="true">'
    + '<span class="tile-icon">'+(TOPIC_ICON[t]||"")+'</span></span>'
    + '<span class="tile-name">'+esc(t)+'</span>'
    + '<span class="tile-count">'+TOPIC_COUNT[t].toLocaleString()+' idioms</span></button>').join("");
}
function renderStarMap(){
  const lit = Math.min(24, learned.size);
  let s = '<svg viewBox="0 0 200 34" aria-hidden="true">';
  for(let i=0;i<24;i++){
    const x = 8+(i%12)*16, y = 9+Math.floor(i/12)*16;
    s += '<circle cx="'+x+'" cy="'+y+'" r="'+(i<lit?3.5:2.2)+'" fill="'+(i<lit?'var(--accent)':'var(--border2)')+'"/>';
  }
  $("#starMap").innerHTML = s+'</svg>';
  $("#starLabel").textContent = learned.size.toLocaleString()+(learned.size===1?" star lit":" stars lit");
}
'''

JS_EVENTS = r'''
/* ---------- illustrated edition: events ---------- */
function syncTopicTiles(){
  $("#topicTiles").querySelectorAll("button").forEach(x => x.classList.toggle("active",x.dataset.topic===state.topic));
}
$("#topicTiles").addEventListener("click", e => {
  const b = e.target.closest("[data-topic]"); if(!b) return;
  const t = b.dataset.topic;
  state.topic = state.topic===t ? "ALL" : t; state.page=1; state.view="all";
  $("#topicChips").querySelectorAll("button").forEach(x => x.classList.toggle("active",x.dataset.topic===state.topic));
  $("#viewTabs").querySelectorAll("button").forEach(x => x.classList.toggle("active",x.dataset.view==="all"));
  syncTopicTiles(); renderResults(); renderActiveFilters();
  document.getElementById("atlasSec").scrollIntoView({behavior:"smooth",block:"start"});
});
$("#topicsAll").addEventListener("click", () => {
  state.topic="ALL"; state.page=1;
  $("#topicChips").querySelectorAll("button").forEach(x => x.classList.remove("active"));
  syncTopicTiles(); renderResults(); renderActiveFilters();
});
$("#heroStart").addEventListener("click", () => document.getElementById("atlasSec").scrollIntoView({behavior:"smooth",block:"start"}));
$("#heroSurprise").addEventListener("click", () => openDetail(DATA[Math.floor(Math.random()*DATA.length)].id));
$("#studyBtn").addEventListener("click", () => startPractice("quiz"));
$("#quickNav").addEventListener("click", e => {
  const b = e.target.closest("[data-go]"); if(!b) return;
  const g = b.dataset.go;
  if(g==="practice"){ startPractice("quiz"); return; }
  if(g==="saved"){
    state.view="fav"; state.page=1;
    $("#viewTabs").querySelectorAll("button").forEach(x => x.classList.toggle("active",x.dataset.view==="fav"));
    renderResults();
  }
  const el = document.getElementById(g==="saved"?"atlasSec":g);
  if(el) el.scrollIntoView({behavior:"smooth",block:"start"});
});
'''

HERO_OLD = r'''  <section class="hero">
    <div class="wrap">
      <div class="hero-top">
        <div>
          <p class="eyebrow">Idioms of the day &middot; <span id="todayLabel"></span></p>
          <h1>Speak American, <em>one idiom at a time.</em></h1>
          <p class="lede">3,001 everyday expressions, explained in plain English. Built for learners who want to understand what people actually mean.</p>
        </div>
        <div class="hero-stats">
          <div class="stat"><b id="statTotal">0</b><span>idioms</span></div>
          <div class="stat"><b id="statFav">0</b><span>saved</span></div>
          <div class="stat"><b id="statLearned">0</b><span>learned</span></div>
        </div>
      </div>
      <div class="daily" id="dailyGrid"></div>
    </div>
  </section>'''

HERO_NEW = r'''  <section class="hero" id="heroSec">
    <div class="wrap">
      <div class="hero-poster">
        <div class="hero-copy">
          <p class="eyebrow">An illustrated atlas of American English &middot; <span id="todayLabel"></span></p>
          <h1>Every idiom has <em>a picture in your head.</em></h1>
          <p class="lede">3,001 everyday expressions explained in plain English — with topic illustrations, listening, daily picks and practice, made for ESL learners.</p>
          <div class="hero-cta">
            <button class="btn accent" id="heroStart">Start exploring</button>
            <button class="btn" id="heroSurprise">Surprise me</button>
          </div>
        </div>
      </div>
      <div class="hero-stats">
        <div class="stat"><b id="statTotal">0</b><span>idioms</span></div>
        <div class="stat"><b id="statFav">0</b><span>saved</span></div>
        <div class="stat"><b id="statLearned">0</b><span>learned</span></div>
        <div class="stat starmap"><div class="starmap-svg" id="starMap"></div><span id="starLabel">0 stars lit</span></div>
      </div>
    </div>
  </section>'''

NEW_SECTIONS = r'''  <section class="today-section" id="todaySec">
    <div class="wrap">
      <div class="banner">
        <div class="banner-art"><img id="todayArt" alt="A sunrise with three star cards and an alarm clock" loading="lazy"></div>
        <div class="banner-copy">
          <p class="banner-kicker">A little, every day</p>
          <h2>Three idioms, picked for today.</h2>
          <p>The same three all day, a fresh set tomorrow. Listen, save one, or tap a card to see the full meaning.</p>
        </div>
      </div>
      <div class="daily" id="dailyGrid"></div>
    </div>
  </section>

  <section class="topics-section" id="topicsSec">
    <div class="wrap">
      <div class="section-head">
        <div><h2>Browse by topic</h2><p>15 illustrated collections — tap a picture to filter the atlas.</p></div>
        <button class="btn subtle small" id="topicsAll">Show all idioms</button>
      </div>
      <div class="topic-grid" id="topicTiles"></div>
    </div>
  </section>

  <section class="study-cta" id="studySec">
    <div class="wrap">
      <div class="banner">
        <div class="banner-art"><img id="practiceArt" alt="Flash cards, a pencil, a trophy and a lightbulb" loading="lazy"></div>
        <div class="banner-copy">
          <p class="banner-kicker">Make it stick</p>
          <h2>Flashcards &amp; quiz, on any set.</h2>
          <p>Practise exactly what you are browsing — a search, one topic, one letter, or just the idioms you saved.</p>
          <div class="hero-cta"><button class="btn accent" id="studyBtn">Start practice</button></div>
        </div>
      </div>
    </div>
  </section>

'''

SUBBAR = r'''
<div class="subbar">
  <div class="wrap subbar-inner">
    <nav class="quicknav" id="quickNav" aria-label="Quick navigation">
      <button data-go="todaySec"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>Today</button>
      <button data-go="topicsSec"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>Topics</button>
      <button data-go="atlasSec"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 6l1.6 4.4L18 12l-4.4 1.6L12 18l-1.6-4.4L6 12l4.4-1.6L12 6z"/></svg>Atlas</button>
      <button data-go="practice" class="primary"><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M8 10l2 2 4-4"/></svg>Practice</button>
      <button data-go="saved"><svg viewBox="0 0 24 24"><path d="M12 3l2.7 5.5 6 .9-4.35 4.25 1.03 6-5.38-2.83L6.62 19.6l1.03-6L3.3 9.4l6-.9L12 3z"/></svg>My idioms</button>
    </nav>
    <span class="subbar-note">One word at a time &middot; progress stays on this device</span>
  </div>
</div>
'''

BRAND_OLD = '      <span class="brand-mark">&ldquo;</span>'
BRAND_NEW = ('      <span class="brand-mark"><svg viewBox="0 0 24 24" aria-hidden="true">'
             '<circle cx="12" cy="12" r="9"/>'
             '<path d="M12 5.5l1.7 4.8 4.8 1.7-4.8 1.7L12 18.5l-1.7-4.8L5.5 12l4.8-1.7L12 5.5z"/>'
             '</svg></span>')


def sub(old, new, label, count=1):
    global html
    n = html.count(old)
    if n != count:
        raise SystemExit(f"{label}: expected {count} match(es), found {n}")
    html = html.replace(old, new, count)


sub('<html lang="en" data-theme="dark">', '<html lang="en" data-theme="light">', "html theme")
sub('savedTheme || "dark"', 'savedTheme || "light"', "default theme")
sub('      <kbd>/</kbd>\n    </div>', '      <kbd>&#8984;K /</kbd>\n    </div>', "search hint")
sub(BRAND_OLD, BRAND_NEW, "brand mark")
sub(HERO_OLD, HERO_NEW, "hero section")
sub('</header>\n', '</header>\n' + SUBBAR, "subbar")
sub('  <section class="explore wrap">', NEW_SECTIONS + '  <section class="explore wrap" id="atlasSec">', "new sections")
sub('<div class="results-head">', '<div class="results-head" id="resultsHead">', "results id")

# artwork payload
art_tag = '<script id="art-data" type="application/json">' + json.dumps(art, separators=(",", ":")) + '</script>\n'
sub('<script id="idiom-data" type="application/json">', art_tag + '<script id="idiom-data" type="application/json">', "art payload")

# CSS appended after the original stylesheet
sub('</style>\n</head>', '</style>\n<style id="illustrated">\n' + CSS + '</style>\n</head>', "css")

# JS: artwork + maps after DATA
sub('const DATA = JSON.parse(document.getElementById("idiom-data").textContent);',
    'const DATA = JSON.parse(document.getElementById("idiom-data").textContent);\n' + JS_MAPS, "js maps")

# JS: event handlers before init
sub('/* ---------- init ---------- */', JS_EVENTS + '\n/* ---------- init ---------- */', "js events")

# JS: wire the two banner images + icon badge + star map + tile sync
sub('  $("#footCount").textContent = DATA.length.toLocaleString();\n}',
    '  $("#footCount").textContent = DATA.length.toLocaleString();\n  renderStarMap();\n}', "stats hook")
sub("'<div class=\"card-head\"><span class=\"level lv'+x.level+'\">'+LEVEL_NAME[x.level]+'</span>'",
    "'<div class=\"card-head\"><span class=\"cat-badge\" title=\"'+esc(x.cat)+'\">'+(TOPIC_ICON[x.cat]||'')+'</span>'"
    "+'<span class=\"level lv'+x.level+'\">'+LEVEL_NAME[x.level]+'</span>'", "card badge")
sub('renderRail(); renderDaily(); updateStats(); renderResults();',
    '$("#todayArt").src = ART.today; $("#practiceArt").src = ART.practice;\n'
    'renderRail(); renderTopicTiles(); renderDaily(); updateStats(); renderResults();', "init")
sub('  $("#topicChips").querySelectorAll("button").forEach(x => x.classList.remove("active"));\n  $("#letters")',
    '  $("#topicChips").querySelectorAll("button").forEach(x => x.classList.remove("active"));\n'
    '  syncTopicTiles();\n  $("#letters")', "reset sync")
sub('  $("#topicChips").querySelectorAll("button").forEach(x => x.classList.toggle("active",x.dataset.topic===state.topic));\n  renderResults();\n});',
    '  $("#topicChips").querySelectorAll("button").forEach(x => x.classList.toggle("active",x.dataset.topic===state.topic));\n'
    '  syncTopicTiles();\n  renderResults();\n});', "topic chips sync")
sub('  if(e.key==="/" && !typing && !$("#overlay").classList.contains("open")){ e.preventDefault(); $("#q").focus(); }',
    '  if((e.metaKey||e.ctrlKey) && e.key.toLowerCase()==="k"){ e.preventDefault(); $("#q").focus(); }\n'
    '  if(e.key==="/" && !typing && !$("#overlay").classList.contains("open")){ e.preventDefault(); $("#q").focus(); }', "cmd-k")

ROOT.write_text(html, encoding="utf-8")
print(f"OK  index.html = {len(html.encode('utf-8')):,} bytes; embedded {len(art)} images")
