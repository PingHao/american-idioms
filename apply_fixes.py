#!/usr/bin/env python3
"""One-shot patcher for the review fixes (a), (b) and (c).

Rebuild chain from a pristine backup:
    /tmp/idiom-atlas-base.html -> apply_design.py -> build_data.py -> apply_fixes.py

build_data.py only replaces the <script id="idiom-data"> block, so it is safe
to re-run at any point (verified byte-identical after this patcher has run).

(a) dark theme: paper/ink tokens become theme-aware; hero scrim, eyebrow and
    the primary CTA all follow --accent instead of hard-coded cream/coral.
(b) Essentials UI: example sentences, alternate senses, an Essentials
    collection tab, daily picks drawn from the curated set, dynamic counts.
(c) topic tiles: distinct stronger tints plus a per-topic hue rotation so the
    five reused illustrations read as different collections.

Refuses to run twice. Only the HTML shell is touched - the embedded idiom-data
and art-data blocks are left alone, so build_data.py can still be re-run.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).with_name("index.html")
html = ROOT.read_text(encoding="utf-8")

if 'id="essentials-layer"' in html:
    sys.exit("Already applied. Restore index.html from the pre-fix build first.")


def sub(old, new, label, count=1):
    global html
    found = html.count(old)
    if found != count:
        sys.exit(f"{label}: expected {count} match(es), found {found}\n  {old[:110]!r}")
    html = html.replace(old, new, count)
    print(f"  ok  {label}")


CSS = r'''
/* ============ Review fixes: theme, tiles, Essentials ============ */
:root{
  --paper:#16233C; --paper-line:#2E4261; --ink:#F7F1E5; --ink2:#AEBBD0;
  --paper-accent:#F2A65A;
  --paper-btn-bg:rgba(255,255,255,.10); --paper-btn-border:rgba(247,241,229,.26);
  --hero-scrim:linear-gradient(90deg,rgba(17,28,49,.97) 0%,rgba(17,28,49,.95) 38%,rgba(17,28,49,.76) 55%,rgba(17,28,49,0) 74%);
  --hero-scrim-m:linear-gradient(180deg,rgba(17,28,49,.97) 0%,rgba(17,28,49,.94) 52%,rgba(17,28,49,.30) 100%);
}
html[data-theme="light"]{
  --paper:#FBF6EA; --paper-line:#E7DCC7; --ink:#1D2A44; --ink2:#4C5872;
  --paper-accent:#B8552D;
  --paper-btn-bg:rgba(255,255,255,.78); --paper-btn-border:rgba(29,42,68,.20);
  --hero-scrim:linear-gradient(90deg,rgba(251,246,234,.98) 0%,rgba(251,246,234,.97) 38%,rgba(251,246,234,.78) 55%,rgba(251,246,234,0) 74%);
  --hero-scrim-m:linear-gradient(180deg,rgba(251,246,234,.97) 0%,rgba(251,246,234,.94) 52%,rgba(251,246,234,.34) 100%);
}
.hero-poster{background-image:var(--hero-scrim),var(--img-hero)}
.hero .eyebrow,.banner-kicker{color:var(--paper-accent)}
.hero h1 em{color:var(--paper-accent)}
.hero-poster .btn,.banner-copy .btn{background:var(--paper-btn-bg);border-color:var(--paper-btn-border)}
.hero-poster .btn.accent,.banner-copy .btn.accent{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
@media (max-width:720px){.hero-poster{background-image:var(--hero-scrim-m),var(--img-hero)}}

/* topic tiles: distinct colour identities for the five reused illustrations */
.tile-art::after{opacity:.30}
.tile-art img{filter:hue-rotate(var(--tile-hue,0deg)) saturate(1.06)}

/* Essentials: example sentences and alternate senses */
.head-tools{display:flex;gap:8px;flex-wrap:wrap}
.card .eg{font:italic 400 11.5px/1.5 Georgia,serif;color:var(--faint);margin:7px 0 0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.detail-example{margin:0 0 14px;padding:13px 15px;border-radius:12px;background:var(--accent-soft);border-left:3px solid var(--accent)}
.detail-example .eg-label,.detail-alts .eg-label{display:block;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;font-weight:700;color:var(--accent);margin-bottom:6px}
.detail-example p{margin:0;font:italic 400 15px/1.6 Georgia,serif;color:var(--text)}
.detail-alts{margin:0 0 16px;padding:11px 14px;border-radius:12px;background:var(--surface2);border:1px solid var(--border)}
.detail-alts .eg-label{color:var(--muted)}
.detail-alts p{margin:0 0 6px;font-size:13px;color:var(--muted);line-height:1.55}
.detail-alts p:last-child{margin-bottom:0}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}*{transition:none!important;animation:none!important}}
'''

print("CSS / HTML:")
sub('</style>\n</head>', '</style>\n<style id="essentials-layer">\n' + CSS + '</style>\n</head>', "css block")

# The original illustrated block hard-coded a light paper palette on :root,
# which overrode dark mode. Drop it: both themes are defined by the new layer.
sub('  --shadow:0 18px 44px rgba(0,0,0,.42);\n  --paper:#FBF6EA; --paper-line:#E7DCC7; --ink:#1D2A44; --ink2:#4C5872;\n}\n',
    '  --shadow:0 18px 44px rgba(0,0,0,.42);\n}\n',
    "remove stale paper tokens")

sub('<meta name="description" content="3,001 American idioms with plain-English meanings. Made for ESL learners.">',
    '<meta name="description" content="American idioms with plain-English meanings and example sentences. Made for ESL learners.">',
    "meta description")

sub('<p class="lede">3,001 everyday expressions explained in plain English — with topic illustrations, listening, daily picks and practice, made for ESL learners.</p>',
    '<p class="lede"><span id="heroCount"></span> everyday expressions explained in plain English — with example sentences for the essentials, topic illustrations, listening, daily picks and practice, made for ESL learners.</p>',
    "hero lede")

sub('        <button class="btn subtle small" id="topicsAll">Show all idioms</button>',
    '        <div class="head-tools"><button class="btn subtle small" id="essentialsBtn">50 essentials &amp; examples</button><button class="btn subtle small" id="topicsAll">Show all idioms</button></div>',
    "essentials button")

sub('''          <button data-view="all" class="active">All idioms</button>
          <button data-view="fav">&#9733; Saved <span id="tabFav">0</span></button>
          <button data-view="learned">&#10003; Learned <span id="tabLearned">0</span></button>''',
    '''          <button data-view="all" class="active">All idioms</button>
          <button data-view="essentials">&#9670; Essentials <span id="tabEss">0</span></button>
          <button data-view="fav">&#9733; Saved <span id="tabFav">0</span></button>
          <button data-view="learned">&#10003; Learned <span id="tabLearned">0</span></button>''',
    "collection tabs")

sub('<div><b>Source:</b> American Idiomology &mdash; Well Over 2500 American Idioms (2019, HOF Publications). Personal / educational study tool.</div>',
    '<div><b>Source:</b> American Idiomology &mdash; Well Over 2500 American Idioms (2019, HOF Publications), plus 50 editor-written essentials with examples. Personal / educational study tool.</div>',
    "footer source line")

OLD_ABOUT = (
    "    + '<li>'+DATA.length.toLocaleString()+' idioms were extracted from the source\\'s 3,002 numbered entries. One stray source fragment was removed.</li>'\n"
    "    + '<li>Six entries had no definition and four were cut off mid-sentence in the source; those ten were completed by the editor and are flagged in the detail view.</li>'"
)
NEW_ABOUT = (
    "    + '<li>'+DATA.length.toLocaleString()+' idioms in total. The source\\'s 3,002 numbered entries yielded 3,001 usable idioms after one stray fragment was removed.</li>'\n"
    "    + '<li>16 entries listed twice in the source have been merged into one card; the other senses appear in the detail view.</li>'\n"
    "    + '<li><strong>50 Essentials</strong> are a separate editor-written layer: common idioms the book omits, with clearer meanings and a real example sentence for each. Open them from the Essentials tab.</li>'\n"
    "    + '<li>Six entries had no definition and four were cut off mid-sentence in the source; those ten were completed by the editor and are flagged in the detail view.</li>'"
)
sub(OLD_ABOUT, NEW_ABOUT, "about data notes")

print("JS:")
sub('''const TILE_TINT = {
  "Everyday Expressions":"#E0A23B", "Time & Speed":"#D98324", "Success & Failure":"#C9A227",
  "Work & Business":"#2F7FA8", "Money & Value":"#3E9B76", "Talk & Truth":"#D2603C",
  "Mind & Ideas":"#7A68B8", "Health & Body":"#D05A72", "Feelings & Mood":"#E07A9B",
  "Places & Travel":"#2E8C9E", "Friends & Family":"#C97B3C", "People & Character":"#5A7FB5",
  "Animals & Weather":"#4E9D8C", "Food & Drink":"#C25B3A", "Sports & Games":"#3F8F5B"
};''',
    '''const TILE_TINT = {
  "Everyday Expressions":"#F2B134", "Time & Speed":"#E4572E", "Success & Failure":"#C6A015",
  "Work & Business":"#1F7A8C", "Money & Value":"#2E8B57", "Talk & Truth":"#D64550",
  "Mind & Ideas":"#6C4FB6", "Health & Body":"#C2185B", "Feelings & Mood":"#E86A9A",
  "Places & Travel":"#0E7C86", "Friends & Family":"#B5651D", "People & Character":"#3457B5",
  "Animals & Weather":"#2F9E6F", "Food & Drink":"#D2691E", "Sports & Games":"#4A7C2F"
};
const TILE_HUE = {
  "Everyday Expressions":0, "Time & Speed":38, "Success & Failure":72,
  "Work & Business":205, "Money & Value":150, "Talk & Truth":330,
  "Mind & Ideas":265, "Health & Body":300, "Feelings & Mood":285,
  "Places & Travel":185, "Friends & Family":25, "People & Character":225,
  "Animals & Weather":120, "Food & Drink":15, "Sports & Games":95
};''',
    "tile tints and hues")

sub("""    '<button class="topic-tile" data-topic="'+esc(t)+'" style="--tile-tint:'+(TILE_TINT[t]||"#DC5C36")+'">'""",
    """    '<button class="topic-tile" data-topic="'+esc(t)+'" style="--tile-tint:'+(TILE_TINT[t]||"#DC5C36")+';--tile-hue:'+(TILE_HUE[t]||0)+'deg">'""",
    "tile inline vars")

sub('''const LEVEL_COUNT = {1:0,2:0,3:0};
DATA.forEach(x => LEVEL_COUNT[x.level]++);''',
    '''const LEVEL_COUNT = {1:0,2:0,3:0};
DATA.forEach(x => LEVEL_COUNT[x.level]++);
const ESS_COUNT = DATA.filter(x => x.curated).length;''',
    "essentials count")

sub('  const u = new SpeechSynthesisUtterance(x.term + ". " + x.def);',
    '  const u = new SpeechSynthesisUtterance(x.term + ". " + x.def + (x.example ? ". For example: " + x.example : ""));',
    "speak includes example")

sub('''    if(state.view==="fav" && !fav.has(x.id)) return false;
    if(state.view==="learned" && !learned.has(x.id)) return false;
    if(state.letter!=="ALL" && x.letter!==state.letter) return false;
    if(state.topic!=="ALL" && !x.cats.includes(state.topic)) return false;
    if(state.level && x.level!==state.level) return false;
    if(q && !x.term.toLowerCase().includes(q) && !x.def.toLowerCase().includes(q)) return false;''',
    '''    if(state.view==="fav" && !fav.has(x.id)) return false;
    if(state.view==="learned" && !learned.has(x.id)) return false;
    if(state.view==="essentials" && !x.curated) return false;
    if(state.letter!=="ALL" && x.letter!==state.letter) return false;
    if(state.topic!=="ALL" && !x.cats.includes(state.topic)) return false;
    if(state.level && x.level!==state.level) return false;
    if(q){
      const hay = (x.term+" "+x.def+" "+(x.example||"")+" "+(x.alts?x.alts.join(" "):"")).toLowerCase();
      if(!hay.includes(q)) return false;
    }''',
    "filtering: essentials + search examples/alts")

sub("""    + '<p class="def">'+highlight(x.def,state.q.trim())+'</p>'""",
    """    + '<p class="def">'+highlight(x.def,state.q.trim())+'</p>'
    + (x.example ? '<p class="eg">&ldquo;'+esc(x.example)+'&rdquo;</p>' : '')""",
    "example line on cards")

sub('  const picks = shuffle(DATA,hashCode(key)).slice(0,3);',
    '''  const pool = DATA.filter(x => x.curated);
  const picks = shuffle(pool.length>=3 ? pool : DATA,hashCode(key)).slice(0,3);''',
    "daily picks from essentials")

sub('  if(state.view!=="all") pills.push(["view",state.view==="fav"?"Saved":"Learned"]);',
    '  if(state.view!=="all") pills.push(["view",state.view==="fav"?"Saved":state.view==="learned"?"Learned":"Essentials"]);',
    "active filter label")

sub('  const labels = {all:"All idioms",fav:"Saved idioms",learned:"Learned idioms"};',
    '  const labels = {all:"All idioms",fav:"Saved idioms",learned:"Learned idioms",essentials:"Essential idioms"};',
    "results title")

sub('''  $("#footCount").textContent = DATA.length.toLocaleString();
  renderStarMap();''',
    '''  $("#footCount").textContent = DATA.length.toLocaleString();
  $("#heroCount").textContent = DATA.length.toLocaleString();
  $("#tabEss").textContent = ESS_COUNT;
  renderStarMap();''',
    "dynamic hero + essentials counts")

sub("""    + '<p class="detail-def">'+esc(x.def)+'</p>'""",
    """    + '<p class="detail-def">'+esc(x.def)+'</p>'
    + (x.example ? '<div class="detail-example"><span class="eg-label">Example</span><p>&ldquo;'+esc(x.example)+'&rdquo;</p></div>' : '')
    + (x.alts && x.alts.length ? '<div class="detail-alts"><span class="eg-label">Also used to mean</span>'+x.alts.map(a => '<p>'+esc(a)+'</p>').join("")+'</div>' : '')""",
    "detail: example and alternate senses")

sub("""    + '<span class="meta-chip">'+x.words+' words</span><span class="meta-chip">#'+x.id+' in source</span>'""",
    """    + '<span class="meta-chip">'+x.words+' words</span><span class="meta-chip">'+(x.src==="essentials"?'Essentials &middot; editor-added':'#'+x.id+' in source')+'</span>'""",
    "detail: source chip")

sub("""    + (x.note ? '<div class="editor-note">This definition was missing or cut off in the source document and has been completed by the editor.</div>' : '')""",
    """    + (x.curated ? '<div class="editor-note">Essentials: the plain-English meaning and example here were written for learners.</div>'
      : x.note ? '<div class="editor-note">This definition was missing or cut off in the source document and has been completed by the editor.</div>' : '')""",
    "detail: provenance note")

sub('''$("#topicsAll").addEventListener("click", () => {
  state.topic="ALL"; state.page=1;
  $("#topicChips").querySelectorAll("button").forEach(x => x.classList.remove("active"));
  syncTopicTiles(); renderResults(); renderActiveFilters();
});''',
    '''$("#topicsAll").addEventListener("click", () => {
  state.topic="ALL"; state.page=1;
  $("#topicChips").querySelectorAll("button").forEach(x => x.classList.remove("active"));
  syncTopicTiles(); renderResults(); renderActiveFilters();
});
$("#essentialsBtn").addEventListener("click", () => {
  state.q=""; state.letter="ALL"; state.topic="ALL"; state.level=0; state.view="essentials"; state.sort="az"; state.page=1;
  $("#q").value=""; $("#clearQ").hidden=true; $("#sortSel").value="az";
  $("#topicChips").querySelectorAll("button").forEach(x => x.classList.remove("active"));
  $("#letters").querySelectorAll("button").forEach(x => x.classList.toggle("active",x.dataset.letter==="ALL"));
  $("#levelBtns").querySelectorAll("button").forEach(x => x.classList.toggle("active",x.dataset.level==="0"));
  $("#viewTabs").querySelectorAll("button").forEach(x => x.classList.toggle("active",x.dataset.view==="essentials"));
  syncTopicTiles(); renderResults(); renderActiveFilters();
  document.getElementById("atlasSec").scrollIntoView({behavior:"smooth",block:"start"});
});''',
    "essentials button handler")

ROOT.write_text(html, encoding="utf-8")
print(f"OK  index.html = {len(html.encode('utf-8')):,} bytes")
