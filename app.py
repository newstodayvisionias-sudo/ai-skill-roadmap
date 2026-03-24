"""
╔══════════════════════════════════════════════════════════════════════╗
║   AI SKILL MASTER — Production SaaS App                             ║
║   30-Day Personalized Learning Roadmap Generator                    ║
║   Stack: Streamlit + Groq (llama-3.3-70b-versatile) + fpdf2        ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ════════════════════════════════════════════════════════════════
# IMPORTS
# ════════════════════════════════════════════════════════════════
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
from datetime import datetime
from fpdf import FPDF
import io, re, time, random, base64, textwrap

# ════════════════════════════════════════════════════════════════
# PAGE CONFIG  (must be the first Streamlit call)
# ════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Skill Master — 30-Day Roadmap",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "AI Skill Master — Free Learning Roadmap Generator"},
)

# ════════════════════════════════════════════════════════════════
# SESSION STATE — initialise all keys at startup
# ════════════════════════════════════════════════════════════════
_DEFAULTS = {
    "roadmap_history": [],        # list[dict] – last 5 roadmaps
    "current_roadmap": None,      # raw text from AI
    "current_skill":   "",
    "current_lang":    "hinglish",
    "current_diff":    "beginner",
    "usage_count":     random.randint(14_200, 14_900),
    "cache":           {},        # cache_key → roadmap_text
    "yt_script":       None,
    "show_yt":         False,
    "show_history":    False,
    "regen_seed":      0,
    "skill_input_val": "",
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ════════════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════════════
SKILL_CHIPS = [
    "Python", "Stock Market", "Digital Marketing", "Video Editing",
    "Web Development", "Data Science", "UI/UX Design", "Copywriting",
    "Machine Learning", "Graphic Design", "SEO", "Public Speaking",
    "Forex Trading", "App Development", "Content Writing", "Blogging",
]

LANG_OPTIONS = {
    "🌐 Hinglish": "hinglish",
    "🇬🇧 English":  "english",
    "🇮🇳 Hindi":    "hindi",
}

DIFF_OPTIONS = {
    "🟢 Beginner":      "beginner",
    "🟡 Intermediate":  "intermediate",
    "🔴 Advanced":      "advanced",
}

WEEK_META = [
    {"label": "WEEK 1", "theme": "Foundation",       "color": "#7c6af7", "glow": "rgba(124,106,247,0.30)"},
    {"label": "WEEK 2", "theme": "Core Concepts",    "color": "#f09819", "glow": "rgba(240,152,25,0.30)"},
    {"label": "WEEK 3", "theme": "Intermediate",     "color": "#11998e", "glow": "rgba(17,153,142,0.30)"},
    {"label": "WEEK 4", "theme": "Advanced + Apply", "color": "#ee0979", "glow": "rgba(238,9,121,0.30)"},
]

LANG_INSTRUCTIONS = {
    "hinglish": (
        "Language: Hinglish (mix of Hindi and English, written in Roman/Latin script). "
        "Tone: friendly, motivating, like a dost/mentor. "
        "Hindi words written phonetically in English (e.g. 'Aaj hum seekhenge...')."
    ),
    "english": (
        "Language: Clear, professional Indian English. "
        "Tone: mentor-like, encouraging, structured. "
        "Use simple sentences and avoid unnecessary jargon."
    ),
    "hindi": (
        "Language: Pure Hindi written in Devanagari script. "
        "Tone: motivating, teacher-like. "
        "Use simple, everyday Hindi vocabulary."
    ),
}

DIFF_INSTRUCTIONS = {
    "beginner":     "Assume zero prior knowledge. Start from absolute basics. Explain every concept simply.",
    "intermediate": "Assume basic familiarity. Skip fundamentals. Focus on practical application and projects.",
    "advanced":     "Assume strong foundation. Focus on advanced topics, optimization, and industry best practices.",
}

# ════════════════════════════════════════════════════════════════
# PREMIUM CSS INJECTION
# ════════════════════════════════════════════════════════════════
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=Fraunces:opsz,wght@9..144,700;9..144,900&display=swap');

:root {
    --bg-deep:    #06040f;
    --bg-card:    rgba(255,255,255,0.04);
    --border:     rgba(255,255,255,0.09);
    --accent:     #7c6af7;
    --gold:       #f9d423;
    --text-pri:   #f0eeff;
    --text-sec:   #9b96c8;
    --text-muted: #5c5880;
    --rad-lg:     20px;
    --rad-md:     12px;
    --rad-sm:     8px;
    --trans:      all 0.22s ease;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-pri) !important;
}
.stApp {
    background:
        radial-gradient(ellipse 120% 80% at 50% -20%, #1a0f40, transparent),
        radial-gradient(ellipse 80% 60% at 80% 100%, #0f1f3d, transparent),
        #06040f !important;
}
.block-container {
    max-width: 1400px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
.stDeployButton { display: none !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #06040f; }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }

/* ════ HEADER ════ */
.app-header { text-align: center; padding: 2.5rem 1rem 1.8rem; position: relative; }
.app-header::before {
    content:''; position:absolute; top:0; left:50%; transform:translateX(-50%);
    width:600px; height:180px;
    background: radial-gradient(ellipse, rgba(124,106,247,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.app-title {
    font-family: 'Fraunces', serif !important;
    font-size: clamp(2rem,6vw,3.6rem) !important;
    font-weight: 900 !important;
    line-height: 1.1 !important;
    background: linear-gradient(135deg, #ffffff 30%, #c4b8ff 70%, #7c6af7);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin: 0 0 0.6rem !important;
    letter-spacing: -1.5px !important;
}
.app-subtitle { color: var(--text-sec) !important; font-size: 1.02rem !important; margin:0!important; }

/* ════ STATS BAR ════ */
.stats-bar {
    display:flex; justify-content:center; gap:2.5rem;
    padding: 1rem 2rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--rad-lg);
    margin: 0 0 1.8rem;
    flex-wrap: wrap;
}
.stat-item { text-align:center; }
.stat-num {
    font-family:'Fraunces',serif; font-size:1.55rem; font-weight:700; line-height:1;
    background: linear-gradient(90deg,#f9d423,#ff6b6b);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.stat-label { font-size:0.72rem; color:var(--text-muted); margin-top:0.2rem; letter-spacing:0.5px; text-transform:uppercase; }

/* ════ GLASS CARD ════ */
.glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--rad-lg);
    padding: 1.8rem;
    margin-bottom: 1.4rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 4px 40px rgba(0,0,0,0.3);
    transition: var(--trans);
}
.glass-card:hover { border-color: rgba(124,106,247,0.22); }

/* ════ SECTION LABEL ════ */
.section-label {
    font-size: 0.68rem; font-weight:600; letter-spacing:2px;
    text-transform:uppercase; color:var(--accent);
    margin-bottom:0.8rem; display:flex; align-items:center; gap:0.5rem;
}
.section-label::after {
    content:''; flex:1; height:1px;
    background: linear-gradient(90deg, var(--border), transparent);
}

/* ════ INPUTS ════ */
.stTextInput > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--rad-md) !important;
    color: var(--text-pri) !important;
    font-size: 1.04rem !important;
    transition: var(--trans) !important;
}
.stTextInput > div > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124,106,247,0.18) !important;
    background: rgba(124,106,247,0.05) !important;
}
.stTextInput label p { color: var(--text-sec) !important; font-weight:500 !important; font-size:0.9rem !important; }
input[type="text"] { color:#fff !important; }
input::placeholder { color:var(--text-muted) !important; }

/* ════ SELECT BOX ════ */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--rad-md) !important;
    color: var(--text-pri) !important;

    height: 55px !important;
    display: flex !important;
    align-items: center !important;

    padding: 0 12px !important;
}
.stSelectbox label p { color:var(--text-sec) !important; font-size:0.85rem !important; font-weight:500 !important; }
.stSelectbox label {
    margin-bottom: 4px !important;
}
/* ════ BUTTONS ════ */
div.stButton > button {
    background: linear-gradient(135deg, #7c6af7, #5546c0) !important;
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.96rem !important;
    padding: 0.65rem 1.6rem !important;
    border: none !important;
    border-radius: var(--rad-md) !important;
    transition: var(--trans) !important;
    box-shadow: 0 4px 18px rgba(124,106,247,0.35) !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(124,106,247,0.5) !important;
}
div.stButton > button:active { transform: translateY(0) !important; }
/* chip buttons */
.chip-btn {
    margin-bottom: 6px !important;
    height: auto !important;
}
/* rows ke beech gap control */
div[data-testid="column"] {
    padding-bottom: 0.1rem !important;
}
.chip-btn div.stButton > button {
    width: 100% !important;
    height: 55px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    padding: 0 10px !important;

    background: rgba(124,106,247,0.12) !important;
    border: 1px solid rgba(124,106,247,0.3) !important;
    color: #c4b8ff !important;

    font-size: 0.82rem !important;
    font-weight: 500 !important;

    border-radius: 12px !important;
    box-shadow: none !important;

    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
.chip-btn div.stButton > button:hover {
    background: rgba(124,106,247,0.25) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* generate button */
.gen-btn {
    margin-top: 0px !important;
}
.gen-btn div.stButton > button {
height: 55px !important;
display: flex !important;
align-items: center !important;
justify-content: center !important;
    background: linear-gradient(135deg, #f9d423, #ff6b35) !important;
    color: #1a0f40 !important;
    font-size: 1.02rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    box-shadow: 0 4px 22px rgba(249,212,35,0.3) !important;
}
.gen-btn div.stButton > button:hover {
    box-shadow: 0 8px 30px rgba(249,212,35,0.5) !important;
}

/* ════ DOWNLOAD BUTTON ════ */
div.stDownloadButton > button {
    background: transparent !important;
    border: 1.5px solid var(--gold) !important;
    color: var(--gold) !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    border-radius: var(--rad-md) !important;
    transition: var(--trans) !important;
    box-shadow: none !important;
    width: 100% !important;
}
div.stDownloadButton > button:hover {
    background: rgba(249,212,35,0.09) !important;
    box-shadow: 0 0 18px rgba(249,212,35,0.25) !important;
    transform: translateY(-1px) !important;
}

/* ════ WEEK CARDS ════ */
.week-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    border-radius: var(--rad-lg);
    padding: 1.5rem;
    margin-bottom: 1.1rem;
    position: relative;
    overflow: hidden;
    transition: var(--trans);
}
.week-card:hover { transform: translateY(-2px); }
.week-header {
    font-family: 'Fraunces', serif;
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    flex-wrap: wrap;
}
.week-badge {
    font-size: 0.68rem; font-weight:600; font-family:'DM Sans',sans-serif;
    padding: 0.18rem 0.55rem; border-radius: 99px;
    letter-spacing: 0.5px; text-transform: uppercase;
}
.day-row {
    display:flex; gap:0.75rem; padding:0.5rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.035);
    align-items: flex-start;
}
.day-row:last-of-type { border-bottom: none; }
.day-num {
    font-family:'Fraunces',serif; font-size:0.82rem; font-weight:700;
    min-width:48px; padding-top:0.1rem; flex-shrink:0;
}
.day-text { font-size:0.88rem; line-height:1.65; color:var(--text-pri); flex:1; }
.day-text strong { color: var(--gold); }
.yt-section { margin-top:1rem; padding-top:0.9rem; border-top:1px solid var(--border); }
.yt-label { font-size:0.7rem; color:var(--text-sec); font-weight:600; letter-spacing:1px; text-transform:uppercase; margin-bottom:0.5rem; }
.yt-chip {
    display:inline-block; background:rgba(255,0,0,0.1); border:1px solid rgba(255,80,80,0.25);
    color:#ff8080; font-size:0.78rem; padding:0.25rem 0.65rem; border-radius:99px;
    margin:0.2rem 0.25rem 0.2rem 0;
}

/* ════ OVERVIEW CARD ════ */
.overview-card {
    background: linear-gradient(135deg, rgba(124,106,247,0.12), rgba(124,106,247,0.03));
    border: 1px solid rgba(124,106,247,0.22);
    border-radius: var(--rad-lg);
    padding: 1.5rem;
    margin-bottom: 1.4rem;
    position: relative; overflow: hidden;
}
.overview-card::after {
    content:'📌'; position:absolute; top:1rem; right:1.4rem;
    font-size:2.8rem; opacity:0.1; pointer-events:none;
}
.overview-title {
    font-family:'Fraunces',serif; font-size:0.85rem; font-weight:700;
    color:#c4b8ff; margin-bottom:0.6rem;
    text-transform:uppercase; letter-spacing:1px;
}
.overview-text { font-size:0.92rem; line-height:1.85; color:var(--text-pri); }

/* ════ MOTIVATION CARD ════ */
.moti-card {
    background: linear-gradient(135deg, rgba(249,212,35,0.07), rgba(255,107,53,0.05));
    border: 1px solid rgba(249,212,35,0.18);
    border-radius: var(--rad-lg);
    padding: 1.5rem 1.8rem;
    margin: 1.4rem 0;
    text-align: center;
}
.moti-icon { font-size:2.2rem; margin-bottom:0.5rem; }
.moti-text { font-size:0.95rem; line-height:1.85; color:var(--text-pri); font-style:italic; }

/* ════ HISTORY ITEM ════ */
.history-item {
    display:flex; align-items:center; justify-content:space-between;
    padding:0.75rem 1rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    border-radius: var(--rad-sm);
    margin-bottom: 0.5rem;
    transition: var(--trans);
}
.history-item:hover { border-color:rgba(124,106,247,0.3); background:rgba(124,106,247,0.06); }
.history-skill { font-weight:600; font-size:0.88rem; }
.history-meta { font-size:0.72rem; color:var(--text-muted); margin-top:0.15rem; }

/* ════ PREMIUM BANNER ════ */
.premium-banner {
    background: linear-gradient(135deg, rgba(249,212,35,0.07), rgba(255,107,53,0.05));
    border: 1px dashed rgba(249,212,35,0.28);
    border-radius: var(--rad-lg);
    padding: 1.3rem 1.6rem;
    margin: 1.4rem 0;
    display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem;
}
.premium-left h4 { font-family:'Fraunces',serif; font-size:1rem; color:var(--gold); margin:0 0 0.3rem; }
.premium-left p { font-size:0.8rem; color:var(--text-sec); margin:0; }
.premium-tag {
    font-size:0.68rem; font-weight:700; letter-spacing:1px; text-transform:uppercase;
    color:#1a0f40; background:linear-gradient(135deg,#f9d423,#ff6b35);
    padding:0.4rem 1rem; border-radius:99px;
}

/* ════ AD PLACEHOLDER ════ */
.ad-slot {
    background:rgba(255,255,255,0.02); border:1px dashed rgba(255,255,255,0.07);
    border-radius:var(--rad-md); padding:0.9rem; text-align:center;
    color:var(--text-muted); font-size:0.72rem; margin:1.4rem 0; letter-spacing:1px;
}

/* ════ EMPTY STATE ════ */
.empty-state { text-align:center; padding:3.5rem 2rem; color:var(--text-muted); }
.empty-icon { font-size:3.5rem; margin-bottom:0.8rem; opacity:0.55; }
.empty-title { font-family:'Fraunces',serif; font-size:1.3rem; color:var(--text-sec); margin-bottom:0.5rem; }
.empty-desc { font-size:0.9rem; max-width:380px; margin:0 auto; line-height:1.75; }

/* ════ SIDEBAR ════ */
section[data-testid="stSidebar"] {
    background: rgba(6,4,15,0.96) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color:#c9c5f0 !important; }
.sidebar-logo {
    font-family:'Fraunces',serif; font-size:1.35rem; font-weight:900;
    background:linear-gradient(135deg,#fff,#c4b8ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin-bottom:0.4rem;
}
.sidebar-tag {
    display:inline-block; font-size:0.62rem; font-weight:700;
    letter-spacing:1.5px; text-transform:uppercase;
    background:linear-gradient(135deg,#f9d423,#ff6b35);
    color:#1a0f40 !important; padding:0.22rem 0.65rem; border-radius:99px;
    margin-bottom:1.1rem;
}
.step-item { display:flex; gap:0.7rem; padding:0.55rem 0; border-bottom:1px solid rgba(255,255,255,0.05); }
.step-num { font-family:'Fraunces',serif; font-size:1.1rem; font-weight:700; color:var(--accent) !important; min-width:22px; line-height:1; padding-top:0.1rem; }
.step-text { font-size:0.82rem; line-height:1.5; color:#9b96c8 !important; }

/* ════ ALERTS ════ */
div[data-testid="stAlert"] { border-radius:var(--rad-md) !important; border:none !important; }

/* ════ PROGRESS BAR ════ */
.stProgress > div > div > div {
    background: linear-gradient(90deg,#7c6af7,#f9d423) !important;
    border-radius: 99px !important;
}

/* ════ RESPONSIVE ════ */
@media (max-width:768px) {
    .stats-bar { gap:1.2rem; }
    .stat-num { font-size:1.2rem; }
    .glass-card, .week-card { padding:1.1rem; }
    .day-num { min-width:38px; font-size:0.76rem; }
    .app-title { letter-spacing:-0.5px !important; }
}
@media (max-width:480px) {
    .premium-banner { flex-direction:column; }
}
/* FIX: row gap */
div.row-widget.stHorizontal {
    gap: 6px !important;
}

/* FIX: align generate button with selectbox */
div[data-testid="stHorizontalBlock"] {
    align-items: end !important;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# HELPER — JS Clipboard Button
# ════════════════════════════════════════════════════════════════
def clipboard_button(text: str, label: str = "📋 Copy to Clipboard", key: str = "cb"):
    encoded = base64.b64encode(text.encode("utf-8")).decode()
    components.html(f"""
<style>
  #cbtn_{key} {{
    font-family:'DM Sans','Segoe UI',sans-serif;
    background:transparent;
    border:1.5px solid rgba(124,106,247,0.45);
    color:#c4b8ff;
    font-size:0.86rem; font-weight:600;
    padding:0.52rem 1.1rem;
    border-radius:10px; cursor:pointer;
    transition:all 0.2s ease; width:100%;
    margin-top:4px;
  }}
  #cbtn_{key}:hover {{
    background:rgba(124,106,247,0.14);
    border-color:#7c6af7;
    box-shadow:0 0 12px rgba(124,106,247,0.28);
  }}
</style>
<button id="cbtn_{key}" onclick="
  var dec = atob('{encoded}');
  navigator.clipboard.writeText(dec).then(function(){{
    var b=document.getElementById('cbtn_{key}');
    b.innerText='✅ Copied!'; b.style.borderColor='#43e97b'; b.style.color='#43e97b';
    setTimeout(function(){{
      b.innerText='{label}'; b.style.borderColor='rgba(124,106,247,0.45)'; b.style.color='#c4b8ff';
    }},2200);
  }}).catch(function(){{
    var b=document.getElementById('cbtn_{key}');
    b.innerText='❌ Use Ctrl+C';
  }});
">{label}</button>
""", height=50)


# ════════════════════════════════════════════════════════════════
# HELPER — Build AI Prompt for Roadmap
# ════════════════════════════════════════════════════════════════
def build_roadmap_prompt(skill: str, language: str, difficulty: str) -> str:
    lang_instr = LANG_INSTRUCTIONS[language]
    diff_instr = DIFF_INSTRUCTIONS[difficulty]
    diff_label = difficulty.upper()
    return f"""
You are an elite learning coach and curriculum designer. Create a COMPLETE, highly detailed 30-day roadmap.

SKILL: "{skill}"
LEVEL: {diff_label} — {diff_instr}
{lang_instr}

Follow this FORMAT exactly — no deviations, no preamble:

🎯 SKILL: {skill.upper()} — 30-DAY {diff_label} ROADMAP

📌 OVERVIEW
[4-5 sentences: why this skill matters, what the learner will achieve in 30 days, overall plan]

---

📅 WEEK 1 — FOUNDATION (Day 1–7)
Day 1: [Topic Title] — [2-sentence description of today's task]
Day 2: [Topic Title] — [2-sentence description]
Day 3: [Topic Title] — [2-sentence description]
Day 4: [Topic Title] — [2-sentence description]
Day 5: [Topic Title] — [2-sentence description]
Day 6: [Topic Title] — [2-sentence description]
Day 7: [Weekly Revision + Mini Project] — [Describe the mini project clearly]

🎬 YouTube Search Keywords (Week 1):
1. "[keyword 1]"
2. "[keyword 2]"
3. "[keyword 3]"

---

📅 WEEK 2 — CORE CONCEPTS (Day 8–14)
Day 8: [Topic Title] — [2-sentence description]
Day 9: [Topic Title] — [2-sentence description]
Day 10: [Topic Title] — [2-sentence description]
Day 11: [Topic Title] — [2-sentence description]
Day 12: [Topic Title] — [2-sentence description]
Day 13: [Topic Title] — [2-sentence description]
Day 14: [Weekly Revision + Mini Project] — [Describe the mini project]

🎬 YouTube Search Keywords (Week 2):
1. "[keyword 1]"
2. "[keyword 2]"
3. "[keyword 3]"

---

📅 WEEK 3 — INTERMEDIATE (Day 15–21)
Day 15: [Topic Title] — [2-sentence description]
Day 16: [Topic Title] — [2-sentence description]
Day 17: [Topic Title] — [2-sentence description]
Day 18: [Topic Title] — [2-sentence description]
Day 19: [Topic Title] — [2-sentence description]
Day 20: [Topic Title] — [2-sentence description]
Day 21: [Weekly Revision + Mini Project] — [Describe the mini project]

🎬 YouTube Search Keywords (Week 3):
1. "[keyword 1]"
2. "[keyword 2]"
3. "[keyword 3]"

---

📅 WEEK 4 — ADVANCED + APPLY (Day 22–30)
Day 22: [Topic Title] — [2-sentence description]
Day 23: [Topic Title] — [2-sentence description]
Day 24: [Topic Title] — [2-sentence description]
Day 25: [Topic Title] — [2-sentence description]
Day 26: [Topic Title] — [2-sentence description]
Day 27: [Topic Title] — [2-sentence description]
Day 28: [Topic Title] — [2-sentence description]
Day 29: [Topic Title] — [2-sentence description]
Day 30: [Capstone Project + Career Next Steps] — [Describe final project and what to do after]

🎬 YouTube Search Keywords (Week 4):
1. "[keyword 1]"
2. "[keyword 2]"
3. "[keyword 3]"

---

🏆 30-DAY KE BAAD / AFTER 30 DAYS
[4-5 sentences: what the learner has achieved, opportunities now available, recommended next steps]

💪 MOTIVATIONAL NOTE
[3-4 powerful motivational sentences to inspire the learner to start TODAY]

---
Start directly with 🎯 SKILL. No preamble. No "Here is your roadmap:".
"""


def build_yt_prompt(skill: str, roadmap: str, language: str) -> str:
    lang_instr = LANG_INSTRUCTIONS[language]
    return f"""
You are a top YouTube content creator. Write a complete 5-7 minute video script.
Title: "How to Learn {skill} in 30 Days — FREE Complete Roadmap"
{lang_instr}

Use key highlights from this roadmap:
{roadmap[:1500]}

Script format:
🎬 VIDEO TITLE: [catchy title]
📌 THUMBNAIL TEXT: [5 words max]

[HOOK — 30 seconds]
[INTRO — 45 seconds]
[MAIN CONTENT — Week-by-week highlights, 3-4 minutes]
[CALL TO ACTION — 30 seconds]
[OUTRO — 30 seconds]

Include [B-ROLL SUGGESTION] notes. Be engaging and conversational.
"""


# ════════════════════════════════════════════════════════════════
# HELPER — Parse Roadmap into Sections
# ════════════════════════════════════════════════════════════════
def parse_roadmap(text: str) -> dict:
    result = {"overview": "", "weeks": [], "aftermath": "", "motivation": "", "raw": text}
    try:
        # Overview
        m = re.search(r'📌\s*OVERVIEW\s*\n(.*?)(?=---|\n📅)', text, re.DOTALL | re.IGNORECASE)
        if m:
            result["overview"] = m.group(1).strip()

        # Weeks — split on week markers
        week_blocks = re.split(r'(?=📅\s*WEEK\s*\d)', text)
        for block in week_blocks:
            wm = re.match(r'📅\s*WEEK\s*(\d+)\s*[—–\-]+\s*(.*?)\s*\n', block)
            if not wm:
                continue
            week_num   = int(wm.group(1))
            week_theme = wm.group(2).strip()

            # YouTube keywords
            yt_m = re.search(r'🎬.*?YouTube.*?\n(.*?)(?=---|\n\n📅|\n🏆|\Z)', block, re.DOTALL)
            yt_kws = []
            if yt_m:
                raw_kws = yt_m.group(1)
                yt_kws = re.findall(r'\d+\.\s*"([^"]+)"', raw_kws)
                if not yt_kws:
                    yt_kws = [ln.strip() for ln in re.findall(r'\d+\.\s*(.+)', raw_kws)]
                block_days = block[:yt_m.start()]
            else:
                block_days = block

            # Parse days
            days_raw = re.findall(r'Day\s*(\d+):\s*(.+?)(?=Day\s*\d+:|🎬|---|\Z)', block_days, re.DOTALL)
            parsed_days = []
            for d_num, d_body in days_raw:
                d_body = d_body.strip()
                parts  = re.split(r'\s*[—–\-]{1,3}\s*', d_body, maxsplit=1)
                if len(parts) == 2:
                    parsed_days.append({"num": d_num, "title": parts[0].strip(), "desc": parts[1].strip()})
                else:
                    parsed_days.append({"num": d_num, "title": "", "desc": d_body})

            result["weeks"].append({
                "number": week_num, "theme": week_theme,
                "days": parsed_days, "yt_kws": yt_kws[:3],
            })

        result["weeks"].sort(key=lambda x: x["number"])

        # Aftermath + Motivation
        am = re.search(r'🏆\s*.*?\n(.*?)(?=💪|---|\Z)', text, re.DOTALL)
        if am:
            result["aftermath"] = am.group(1).strip()
        mm = re.search(r'💪\s*.*?NOTE\s*\n(.*?)(?=---|$)', text, re.DOTALL | re.IGNORECASE)
        if not mm:
            mm = re.search(r'💪\s*.*?\n(.*?)(?=---|$)', text, re.DOTALL)
        if mm:
            result["motivation"] = mm.group(1).strip()

    except Exception:
        pass  # graceful fallback to raw text
    return result


# ════════════════════════════════════════════════════════════════
# HELPER — Render Parsed Roadmap as Premium Cards
# ════════════════════════════════════════════════════════════════
def render_roadmap_ui(parsed: dict):
    raw = parsed.get("raw", "")

    # Overview
    if parsed["overview"]:
        st.markdown(f"""
<div class="overview-card">
  <div class="overview-title">📌 Overview</div>
  <div class="overview-text">{parsed['overview']}</div>
</div>""", unsafe_allow_html=True)

    weeks = parsed["weeks"]
    if not weeks:
        # Fallback raw display
        st.markdown(f"""
<div class="glass-card" style="white-space:pre-wrap;font-size:0.9rem;line-height:1.85;">
{raw}
</div>""", unsafe_allow_html=True)
        return

    for i, week in enumerate(weeks):
        meta  = WEEK_META[min(i, 3)]
        color = meta["color"]
        glow  = meta["glow"]

        # Build days HTML
        days_html = ""
        for day in week["days"]:
            title_part = f"<strong>{day['title']}</strong> — " if day["title"] else ""
            days_html += f"""
<div class="day-row">
  <div class="day-num" style="color:{color};">Day {day['num']}</div>
  <div class="day-text">{title_part}{day['desc']}</div>
</div>"""

        # YouTube chips
        yt_html = ""
        if week["yt_kws"]:
            chips  = "".join(f'<span class="yt-chip">🔍 {kw}</span>' for kw in week["yt_kws"])
            yt_html = f'<div class="yt-section"><div class="yt-label">📺 YouTube Search Keywords</div>{chips}</div>'

        badge = f'<span class="week-badge" style="background:rgba(0,0,0,0.35);color:{color};border:1px solid {color}44;">{week["theme"]}</span>'

        st.markdown(f"""
<div class="week-card" style="box-shadow:0 4px 28px {glow};border-color:{color}20;">
  <div style="position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,{color},{color}44);
    border-radius:20px 20px 0 0;"></div>
  <div class="week-header" style="color:{color};">
    📅 Week {week['number']} {badge}
  </div>
  {days_html or f"<p style='color:#9b96c8;font-size:0.88rem;'>{week.get('theme','')}</p>"}
  {yt_html}
</div>""", unsafe_allow_html=True)

    # Aftermath
    if parsed["aftermath"]:
        st.markdown(f"""
<div class="glass-card" style="border-color:rgba(67,233,123,0.22);background:rgba(67,233,123,0.03);">
  <div class="overview-title" style="color:#43e97b;">🏆 30 Days ke Baad — What You've Achieved</div>
  <div class="overview-text">{parsed['aftermath']}</div>
</div>""", unsafe_allow_html=True)

    # Motivation
    if parsed["motivation"]:
        st.markdown(f"""
<div class="moti-card">
  <div class="moti-icon">💪</div>
  <div class="moti-text">{parsed['motivation']}</div>
</div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# HELPER — Generate PDF (fpdf2)
# ════════════════════════════════════════════════════════════════
def generate_pdf(skill: str, text: str) -> bytes:
    def safe(s: str) -> str:
        return s.encode("latin-1", "replace").decode("latin-1")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Title block
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(30, 10, 80)
    pdf.cell(0, 12, safe("AI SKILL MASTER"), ln=True, align="C")
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 10, safe(f"30-Day Roadmap: {skill}"), ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(120, 120, 150)
    pdf.cell(0, 8, safe(f"Generated: {datetime.now().strftime('%d %B %Y')}  |  aiskillmaster.streamlit.app"), ln=True, align="C")
    pdf.ln(5)
    pdf.set_draw_color(124, 106, 247)
    pdf.set_line_width(0.7)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)

    # Body
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(25, 15, 55)

    for raw_line in text.splitlines():
        line    = safe(raw_line)
        stripped = line.strip()
        if not stripped:
            pdf.ln(3)
            continue
        if any(e in raw_line for e in ["📅", "🏆", "💪", "📌", "🎯", "🎬"]):
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(80, 55, 180)
            pdf.ln(4)
            pdf.multi_cell(0, 7, stripped)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(25, 15, 55)
        elif stripped.startswith("Day "):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(60, 40, 140)
            pdf.multi_cell(0, 6, stripped)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(25, 15, 55)
        elif "---" in stripped:
            pdf.set_draw_color(200, 195, 240)
            pdf.set_line_width(0.3)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(3)
        else:
            for chunk in textwrap.wrap(stripped, 100) or [stripped]:
                pdf.multi_cell(0, 6, safe(chunk))

    # Footer
    pdf.ln(8)
    pdf.set_draw_color(124, 106, 247)
    pdf.set_line_width(0.4)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(140, 130, 175)
    pdf.cell(0, 6, safe("Generated by AI Skill Master — Free Learning Roadmap Tool | Powered by Groq AI"), align="C")

    return bytes(pdf.output())


# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🚀 AI Skill Master</div>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-tag">✨ 100% Free Tool</span>', unsafe_allow_html=True)

    st.markdown("### How It Works")
    for num, txt in [
        ("1", "Enter the skill you want to learn"),
        ("2", "Select language & difficulty level"),
        ("3", "Click Generate — AI builds your plan"),
        ("4", "Download as PDF or copy the roadmap"),
    ]:
        st.markdown(f'<div class="step-item"><div class="step-num">{num}</div><div class="step-text">{txt}</div></div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚡ Tech Stack")
    st.markdown(
        '<div style="font-size:0.8rem;color:#9b96c8;line-height:2.1;">'
        '🤖 <b>Groq API</b> — llama-3.3-70b-versatile<br>'
        '🎨 <b>Streamlit</b> — UI Framework<br>'
        '📄 <b>fpdf2</b> — PDF Generation<br>'
        '🔒 <b>st.secrets</b> — Secure API Key</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if st.session_state.roadmap_history:
        n = len(st.session_state.roadmap_history)
        if st.button(f"📚 View History ({n})", use_container_width=True):
            st.session_state.show_history = not st.session_state.show_history

    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.76rem;color:#5c5880;text-align:center;line-height:1.9;">'
        '📖 <i>Developed to help students<br>learn any skill for free</i><br><br>'
        'Made with ❤️ for Indian Students</div>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════
# INJECT CSS (after sidebar so it applies globally)
# ════════════════════════════════════════════════════════════════
inject_css()


# ════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div class="app-header">
  <div class="app-title">AI Skill Master</div>
  <p class="app-subtitle">Koi bhi skill seekho — 30 din mein — Personalized Roadmap ke saath 🚀</p>
</div>""", unsafe_allow_html=True)

# Stats Bar
count = st.session_state.usage_count
st.markdown(f"""
<div class="stats-bar">
  <div class="stat-item"><div class="stat-num">{count:,}+</div><div class="stat-label">Roadmaps Generated</div></div>
  <div class="stat-item"><div class="stat-num">30</div><div class="stat-label">Days Per Plan</div></div>
  <div class="stat-item"><div class="stat-num">100%</div><div class="stat-label">Free Forever</div></div>
  <div class="stat-item"><div class="stat-num">3</div><div class="stat-label">Languages</div></div>
</div>""", unsafe_allow_html=True)

# Top Ad Slot
st.markdown('<div class="ad-slot">📢 ADVERTISEMENT — Google AdSense Placement (728×90)</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# INPUT FORM
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">🎯 Configure Your Roadmap</div>', unsafe_allow_html=True)

# Skill text input (key links to session state)
col_center = st.columns([1,2,1])[1]

with col_center:
    skill_input = st.text_input(
        "🎯 Aap kaunsi Skill seekhna chahte hain?",
        value=st.session_state.skill_input_val,
        placeholder="e.g. Python, Stock Market, Video Editing...",
        max_chars=80,
        key="skill_input_val",
    )
# Skill chips — row 1
st.markdown('<div style="margin:-0.3rem 0 0.6rem;"><span style="font-size:0.7rem;color:var(--text-muted);letter-spacing:1px;text-transform:uppercase;">Quick Select →</span></div>',
            unsafe_allow_html=True)

for i in range(0, len(SKILL_CHIPS), 4):
    row = SKILL_CHIPS[i:i+4]
    cols = st.columns(4)

    for col, skill in zip(cols, row):
        with col:
            st.markdown('<div class="chip-btn">', unsafe_allow_html=True)

            st.button(
                skill,
                key=f"chip_{skill}",
                use_container_width=True,
                on_click=lambda s=skill: st.session_state.update({"skill_input_val": s})
            )

            st.markdown('</div>', unsafe_allow_html=True)




# Language | Difficulty | Generate
col_l, col_d, col_g = st.columns(3)
with col_l:
    lang_label = st.selectbox("🌐 Language", list(LANG_OPTIONS.keys()), index=0, key="sel_lang")
    lang_key   = LANG_OPTIONS[lang_label]
with col_d:
    diff_label = st.selectbox("📊 Difficulty", list(DIFF_OPTIONS.keys()), index=0, key="sel_diff")
    diff_key   = DIFF_OPTIONS[diff_label]
with col_g:
    
    st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
    generate_btn = st.button("✨ Generate Roadmap", use_container_width=True, key="gen_main")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close glass-card


# ════════════════════════════════════════════════════════════════
# GENERATION LOGIC
# ════════════════════════════════════════════════════════════════
if generate_btn:
    skill_clean = st.session_state.skill_input_val.strip()

    if not skill_clean:
        st.markdown("""
<div style="background:rgba(255,107,53,0.1);border:1px solid rgba(255,107,53,0.28);border-radius:12px;
  padding:1rem 1.4rem;color:#ff9070;font-size:0.9rem;margin:0.5rem 0;">
  ⚠️ <strong>Skill name enter karo!</strong> Text box mein type karo ya upar se chip select karo.
</div>""", unsafe_allow_html=True)
    else:
        cache_key = f"{skill_clean}|{lang_key}|{diff_key}|{st.session_state.regen_seed}"

        if cache_key in st.session_state.cache:
            st.session_state.current_roadmap = st.session_state.cache[cache_key]
            st.session_state.current_skill   = skill_clean
            st.session_state.current_lang    = lang_key
            st.session_state.current_diff    = diff_key
            st.info("⚡ Cached result loaded instantly — same skill+language+difficulty!")
        else:
            try:
                client   = Groq(api_key=st.secrets["GROQ_API_KEY"])
                prog_bar = st.progress(0)
                status_p = st.empty()

                for i, msg in enumerate([
                    "🧠 AI aapka personalised plan design kar raha hai...",
                    "📅 Week-by-week schedule taiyaar ho raha hai...",
                    "🎬 YouTube search keywords generate ho rahe hain...",
                    "✨ Final polish lag raha hai — almost done!",
                ]):
                    status_p.markdown(
                        f'<div style="background:rgba(124,106,247,0.1);border:1px solid '
                        f'rgba(124,106,247,0.3);border-radius:12px;padding:0.9rem 1.3rem;'
                        f'color:#c4b8ff;font-size:0.9rem;margin:0.4rem 0;">{msg}</div>',
                        unsafe_allow_html=True,
                    )
                    prog_bar.progress((i + 1) * 22)
                    time.sleep(0.4)

                prog_bar.progress(90)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content":
                            f"You are an expert learning coach. {LANG_INSTRUCTIONS[lang_key]} "
                            "Always follow the exact output format provided. Be specific and actionable."},
                        {"role": "user", "content": build_roadmap_prompt(skill_clean, lang_key, diff_key)},
                    ],
                    temperature=0.72,
                    max_tokens=4096,
                )
                prog_bar.progress(100)
                time.sleep(0.25)
                prog_bar.empty()
                status_p.empty()

                roadmap_text = response.choices[0].message.content

                # Cache & store
                st.session_state.cache[cache_key]  = roadmap_text
                st.session_state.current_roadmap   = roadmap_text
                st.session_state.current_skill     = skill_clean
                st.session_state.current_lang      = lang_key
                st.session_state.current_diff      = diff_key
                st.session_state.yt_script         = None
                st.session_state.show_yt           = False
                st.session_state.usage_count      += 1

                # History
                st.session_state.roadmap_history.insert(0, {
                    "skill": skill_clean, "lang": lang_key, "diff": diff_key,
                    "date":  datetime.now().strftime("%d %b, %I:%M %p"),
                    "text":  roadmap_text,
                })
                st.session_state.roadmap_history = st.session_state.roadmap_history[:5]

            except KeyError:
                st.markdown("""
<div style="background:rgba(255,50,50,0.1);border:1px solid rgba(255,50,50,0.28);border-radius:12px;
  padding:1.1rem 1.4rem;color:#ff7070;">
  🔑 <strong>API Key nahi mili!</strong><br>
  <span style="font-size:0.82rem;">
  Streamlit Cloud → Settings → Secrets mein add karo:<br>
  <code>GROQ_API_KEY = "gsk_xxxxxxxxxxxx"</code>
  </span>
</div>""", unsafe_allow_html=True)

            except Exception as e:
                st.markdown(f"""
<div style="background:rgba(255,50,50,0.1);border:1px solid rgba(255,50,50,0.28);border-radius:12px;
  padding:1.1rem 1.4rem;color:#ff7070;">
  ❌ <strong>Error aaya:</strong> {str(e)[:220]}<br>
  <span style="font-size:0.82rem;">Thodi der baad dobara try karo.</span>
</div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# DISPLAY ROADMAP
# ════════════════════════════════════════════════════════════════
if st.session_state.current_roadmap:
    roadmap_txt = st.session_state.current_roadmap
    skill_name  = st.session_state.current_skill

    st.markdown("---")

    # Header + Regenerate
    rh1, rh2 = st.columns([4, 1])
    with rh1:
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap;margin-bottom:1.4rem;">
  <span style="font-family:'Fraunces',serif;font-size:1.55rem;font-weight:900;color:#fff;">📋 Your 30-Day Roadmap</span>
  <span style="background:rgba(124,106,247,0.18);border:1px solid rgba(124,106,247,0.38);
    border-radius:99px;padding:0.28rem 0.95rem;font-size:0.78rem;font-weight:600;color:#c4b8ff;">
    {skill_name}
  </span>
</div>""", unsafe_allow_html=True)
    with rh2:
        if st.button("🔄 Regenerate", use_container_width=True, key="regen"):
            st.session_state.regen_seed += 1
            old_key = f"{skill_name}|{st.session_state.current_lang}|{st.session_state.current_diff}|{st.session_state.regen_seed - 1}"
            if old_key in st.session_state.cache:
                del st.session_state.cache[old_key]
            st.session_state.current_roadmap = None
            st.session_state.yt_script = None
            st.session_state.show_yt = False
            # Re-trigger: set generate flag via URL param workaround — just show message
            st.info("🔄 Skill naam dobara enter karke Generate click karo for a fresh roadmap!")

    # Render parsed roadmap
    parsed = parse_roadmap(roadmap_txt)
    render_roadmap_ui(parsed)

    st.markdown("---")

    # ── Export & Share Bar ──
    st.markdown('<div class="section-label">⬇️ Export & Share</div>', unsafe_allow_html=True)
    a1, a2, a3 = st.columns(3)

    with a1:
        try:
            pdf_bytes = generate_pdf(skill_name, roadmap_txt)
            st.download_button(
                label="📄 Download PDF",
                data=pdf_bytes,
                file_name=f"{skill_name.replace(' ','_')}_30Day_Roadmap.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_pdf",
            )
        except Exception:
            st.download_button(
                label="📄 Download TXT",
                data=roadmap_txt.encode("utf-8"),
                file_name=f"{skill_name.replace(' ','_')}_Roadmap.txt",
                mime="text/plain",
                use_container_width=True,
            )

    with a2:
        st.download_button(
            label="📝 Download TXT",
            data=roadmap_txt.encode("utf-8"),
            file_name=f"{skill_name.replace(' ','_')}_30Day_Roadmap.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_txt",
        )

    with a3:
        share_str = (
            f"🚀 I generated a FREE 30-Day {skill_name} Roadmap with AI!\n\n"
            f"✅ Day-by-day plan  ✅ YouTube keywords  ✅ Hinglish / English / Hindi\n\n"
            f"Try it → AI Skill Master on Streamlit\n\n"
            f"#AILearning #{''.join(skill_name.split())} #30DayChallenge #FreeEducation"
        )
        st.download_button(
            label="📤 Share Text",
            data=share_str.encode("utf-8"),
            file_name="share_roadmap.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_share",
        )

    # Copy to clipboard
    clipboard_button(roadmap_txt, "📋 Copy Full Roadmap to Clipboard", key="main_cb")

    # ── Tips Card ──
    st.markdown("""
<div class="glass-card" style="border-color:rgba(67,233,123,0.18);background:rgba(67,233,123,0.025);margin-top:1.4rem;">
  <div class="overview-title" style="color:#43e97b;">📌 Daily Success Tips</div>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:0.6rem;font-size:0.86rem;line-height:1.75;color:var(--text-pri);">
    <div>✅ Har din <strong>minimum 1 ghanta</strong> practice karo</div>
    <div>✅ YouTube keywords se <strong>FREE tutorials</strong> dhundho</div>
    <div>✅ Har week end mein <strong>mini project</strong> banao</div>
    <div>✅ Notes banao aur <strong>weekly revision</strong> karo</div>
    <div>✅ <strong>Community</strong> join karo — Discord, Reddit, LinkedIn</div>
    <div>✅ Progress <strong>track karo</strong> — daily check-in jaruri hai</div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════
    # VIRAL FEATURES ROW
    # ════════════════════════════════════════════════════════════
    st.markdown('<div class="section-label">🔥 Viral Features</div>', unsafe_allow_html=True)
    vf1, vf2, vf3 = st.columns(3)

    with vf1:
        st.markdown("""
<div class="glass-card" style="text-align:center;padding:1.3rem;min-height:150px;">
  <div style="font-size:1.9rem;margin-bottom:0.4rem;">🎬</div>
  <div style="font-weight:600;font-size:0.92rem;margin-bottom:0.35rem;">YouTube Script</div>
  <div style="font-size:0.78rem;color:var(--text-sec);">Full 5-min video script generated from your roadmap</div>
</div>""", unsafe_allow_html=True)
        if st.button("Generate Script ▶", use_container_width=True, key="yt_gen"):
            st.session_state.show_yt = True
            st.session_state.yt_script = None

    with vf2:
        st.markdown("""
<div class="glass-card" style="text-align:center;padding:1.3rem;min-height:150px;">
  <div style="font-size:1.9rem;margin-bottom:0.4rem;">📱</div>
  <div style="font-weight:600;font-size:0.92rem;margin-bottom:0.35rem;">Instagram Carousel</div>
  <div style="font-size:0.78rem;color:var(--text-sec);">Auto-generate 10-slide carousel content</div>
  <div style="margin-top:0.7rem;font-size:0.7rem;background:rgba(249,212,35,0.12);border:1px solid rgba(249,212,35,0.28);border-radius:99px;padding:0.2rem 0.65rem;display:inline-block;color:#f9d423;">🔒 Premium — Coming Soon</div>
</div>""", unsafe_allow_html=True)

    with vf3:
        st.markdown("""
<div class="glass-card" style="text-align:center;padding:1.3rem;min-height:150px;">
  <div style="font-size:1.9rem;margin-bottom:0.4rem;">📅</div>
  <div style="font-weight:600;font-size:0.92rem;margin-bottom:0.35rem;">Daily Reminder</div>
  <div style="font-size:0.78rem;color:var(--text-sec);">WhatsApp / Email reminders every day at your time</div>
  <div style="margin-top:0.7rem;font-size:0.7rem;background:rgba(249,212,35,0.12);border:1px solid rgba(249,212,35,0.28);border-radius:99px;padding:0.2rem 0.65rem;display:inline-block;color:#f9d423;">🔒 Premium — Coming Soon</div>
</div>""", unsafe_allow_html=True)

    # YouTube Script Output
    if st.session_state.show_yt:
        if st.session_state.yt_script is None:
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                with st.spinner("🎬 YouTube script likh raha hoon... ek minute!"):
                    yt_resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content":
                                f"You are a top YouTube content creator. {LANG_INSTRUCTIONS[st.session_state.current_lang]}"},
                            {"role": "user", "content": build_yt_prompt(
                                skill_name, roadmap_txt, st.session_state.current_lang
                            )},
                        ],
                        temperature=0.82,
                        max_tokens=2000,
                    )
                st.session_state.yt_script = yt_resp.choices[0].message.content
            except Exception as e:
                st.error(f"Script generation failed: {e}")

        if st.session_state.yt_script:
            st.markdown(f"""
<div class="glass-card" style="border-color:rgba(255,80,80,0.2);background:rgba(255,50,50,0.03);">
  <div class="overview-title" style="color:#ff8080;">🎬 YouTube Script — {skill_name}</div>
  <div style="font-size:0.87rem;line-height:1.9;white-space:pre-wrap;color:var(--text-pri);">{st.session_state.yt_script}</div>
</div>""", unsafe_allow_html=True)
            clipboard_button(st.session_state.yt_script, "📋 Copy Script", key="yt_copy")

    # ── Premium CTA ──
    st.markdown("""
<div class="premium-banner">
  <div class="premium-left">
    <h4>⚡ Upgrade to AI Skill Master Pro</h4>
    <p>Instagram Carousel Generator &nbsp;•&nbsp; Daily WhatsApp Reminders &nbsp;•&nbsp; Progress Tracker &nbsp;•&nbsp; Team Sharing &nbsp;•&nbsp; Ad-Free Experience</p>
  </div>
  <div class="premium-tag">Coming Soon 🚀</div>
</div>""", unsafe_allow_html=True)

    # Bottom Ad Slot
    st.markdown('<div class="ad-slot">📢 ADVERTISEMENT — Google AdSense Placement (728×90 Leaderboard)</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# EMPTY STATE
# ════════════════════════════════════════════════════════════════
else:
    st.markdown("""
<div class="empty-state">
  <div class="empty-icon">🗺️</div>
  <div class="empty-title">Aapka Roadmap Yahaan Dikhega</div>
  <div class="empty-desc">
    Upar apni skill enter karo, language aur difficulty choose karo,
    aur <strong>"Generate Roadmap"</strong> button click karo —
    AI 30 seconds mein aapka personalized plan taiyaar kar dega!
  </div>
</div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# HISTORY SECTION (collapsible via sidebar button)
# ════════════════════════════════════════════════════════════════
if st.session_state.show_history and st.session_state.roadmap_history:
    st.markdown("---")
    st.markdown('<div class="section-label">📚 Recent Roadmaps (Last 5)</div>', unsafe_allow_html=True)

    for idx, item in enumerate(st.session_state.roadmap_history):
        hc1, hc2 = st.columns([5, 1])
        with hc1:
            st.markdown(f"""
<div class="history-item">
  <div>
    <div class="history-skill">🎯 {item['skill']}</div>
    <div class="history-meta">{item['lang'].title()} • {item['diff'].title()} • {item['date']}</div>
  </div>
</div>""", unsafe_allow_html=True)
        with hc2:
            if st.button("Load", key=f"hist_{idx}", use_container_width=True):
                st.session_state.current_roadmap = item["text"]
                st.session_state.current_skill   = item["skill"]
                st.session_state.current_lang    = item["lang"]
                st.session_state.current_diff    = item["diff"]
                st.session_state.show_history    = False
                st.session_state.yt_script       = None
                st.session_state.show_yt         = False
                st.rerun()


# ════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;padding:2rem 1rem 0.5rem;color:var(--text-muted);font-size:0.78rem;line-height:2.1;">
  <span style="font-family:'Fraunces',serif;font-size:0.95rem;color:var(--text-sec);">🚀 AI Skill Master</span><br>
  Powered by Groq + Streamlit &nbsp;|&nbsp; Made with ❤️ for Indian Students &nbsp;|&nbsp; 100% Free Forever<br>
  <span style="font-size:0.7rem;">
    Share this tool with your friends &nbsp;|&nbsp; #AISkillMaster &nbsp;|&nbsp; #FreeEducation
  </span>
</div>""", unsafe_allow_html=True)
