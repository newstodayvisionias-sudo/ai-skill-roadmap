import streamlit as st
from groq import Groq

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Skill Master: 30-Day Roadmap",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* ── Hero Header ── */
.hero-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.hero-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #f9d423, #ff4e50);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
    letter-spacing: -1px;
}
.hero-header p {
    color: #a8a4d4;
    font-size: 1.05rem;
    font-weight: 300;
    margin-top: 0;
}

/* ── Card container ── */
.glass-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 2rem;
    backdrop-filter: blur(10px);
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

/* ── Input label override ── */
label[data-testid="stTextInputLabel"] p,
.stTextInput label {
    color: #e0deff !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
}

/* ── Input box ── */
input[type="text"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1.5px solid rgba(249,212,35,0.4) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-size: 1.05rem !important;
    padding: 0.75rem 1rem !important;
}
input[type="text"]:focus {
    border-color: #f9d423 !important;
    box-shadow: 0 0 0 3px rgba(249,212,35,0.15) !important;
}

/* ── Generate Button ── */
div.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #f9d423, #ff4e50);
    color: #1a1a2e;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(249,212,35,0.3);
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(249,212,35,0.45);
}

/* ── Download Button ── */
div.stDownloadButton > button {
    width: 100%;
    background: transparent;
    color: #f9d423;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    padding: 0.65rem 1.5rem;
    border: 1.5px solid #f9d423;
    border-radius: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-top: 0.8rem;
}
div.stDownloadButton > button:hover {
    background: rgba(249,212,35,0.12);
    box-shadow: 0 0 18px rgba(249,212,35,0.3);
}

/* ── Success / Info boxes ── */
div[data-testid="stAlert"] {
    border-radius: 16px !important;
    font-size: 0.97rem;
    line-height: 1.8;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.85) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] * {
    color: #c9c5f0 !important;
}
.sidebar-badge {
    background: linear-gradient(135deg, #f9d423, #ff4e50);
    color: #1a1a2e !important;
    font-weight: 700;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    display: inline-block;
    margin-bottom: 1rem;
}

/* ── Divider ── */
hr {
    border-color: rgba(255,255,255,0.08) !important;
    margin: 1.5rem 0;
}

/* ── Roadmap output text ── */
.roadmap-text {
    white-space: pre-wrap;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    line-height: 1.9;
    color: #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-badge">✨ FREE TOOL</div>', unsafe_allow_html=True)
    st.markdown("## 🎯 AI Skill Master")
    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown(
        "**Developed to help students learn any skill for free.**\n\n"
        "Yeh tool Groq ke powerful AI engine ka use karke ek "
        "personalized 30-day roadmap banata hai — bilkul FREE! 🚀"
    )
    st.markdown("---")
    st.markdown("### 🛠️ How it Works")
    st.markdown(
        "1. **Skill enter karo** — jo bhi seekhna ho\n"
        "2. **Button click karo** — AI kaam karega\n"
        "3. **Roadmap padho** — Hinglish mein!\n"
        "4. **Download karo** — `.txt` file mein save karo"
    )
    st.markdown("---")
    st.markdown("### ⚡ Powered By")
    st.markdown("🤖 **Groq API** — llama-3.3-70b-versatile\n\n🎨 **Streamlit** — UI Framework")
    st.markdown("---")
    st.caption("Made with ❤️ for Indian Students")

# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>🚀 AI Skill Master</h1>
    <p>Koi bhi skill seekho — 30 din mein — FREE Roadmap ke saath!</p>
</div>
""", unsafe_allow_html=True)

# ── Tip Banner ────────────────────────────────────────────────────────────────
st.info(
    "💡 **Pro Tip:** Skill ka naam jitna specific hoga, roadmap utna hi better banega! "
    "Example: 'Python' ki jagah 'Python for Data Science' try karo."
)

# ── Input Section ─────────────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    skill_input = st.text_input(
        "🎯 Aap kaunsi Skill seekhna chahte hain?",
        placeholder="e.g. Python, Stock Market, Digital Marketing, Video Editing...",
        max_chars=80,
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("✨ Generate Roadmap", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# ── Prompt Builder ────────────────────────────────────────────────────────────
def build_prompt(skill: str) -> str:
    return f"""
Tum ek world-class learning coach ho jo students ko FREE mein koi bhi skill sikhane mein help karta hai.

Ek user ne request ki hai: **"{skill}"** skill seekhni hai 30 dino mein.

Neeche diya gaya format EXACTLY follow karo. Language: Hinglish (Hindi + English mix) — friendly, motivating tone.

---

🎯 SKILL: {skill.upper()} — 30-DAY MASTER ROADMAP

📌 OVERVIEW (3-4 lines mein batao is skill ki importance aur 30 din ka overall plan)

---

📅 WEEK 1 — FOUNDATION (Day 1–7)
[Har din ek clear task/topic do. Format: Day X: [Topic] — [Brief explanation in Hinglish, 1-2 lines]]
Day 1: ...
Day 2: ...
Day 3: ...
Day 4: ...
Day 5: ...
Day 6: ...
Day 7: [Weekly revision + mini project/assignment]

🎬 YouTube Search Keywords (Week 1):
1. "[keyword 1]"
2. "[keyword 2]"
3. "[keyword 3]"

---

📅 WEEK 2 — CORE CONCEPTS (Day 8–14)
Day 8: ...
Day 9: ...
Day 10: ...
Day 11: ...
Day 12: ...
Day 13: ...
Day 14: [Weekly revision + mini project/assignment]

🎬 YouTube Search Keywords (Week 2):
1. "[keyword 1]"
2. "[keyword 2]"
3. "[keyword 3]"

---

📅 WEEK 3 — INTERMEDIATE LEVEL (Day 15–21)
Day 15: ...
Day 16: ...
Day 17: ...
Day 18: ...
Day 19: ...
Day 20: ...
Day 21: [Weekly revision + mini project/assignment]

🎬 YouTube Search Keywords (Week 3):
1. "[keyword 1]"
2. "[keyword 2]"
3. "[keyword 3]"

---

📅 WEEK 4 — ADVANCED + APPLY (Day 22–30)
Day 22: ...
Day 23: ...
Day 24: ...
Day 25: ...
Day 26: ...
Day 27: ...
Day 28: ...
Day 29: ...
Day 30: [Final project/assessment + career next steps]

🎬 YouTube Search Keywords (Week 4):
1. "[keyword 1]"
2. "[keyword 2]"
3. "[keyword 3]"

---

🏆 30-DAY KE BAAD KYA HOGA?
[3-4 lines mein batao student ab kya kar sakta hai, kya achieve kiya, aur aage kahan jaaye]

💪 MOTIVATIONAL NOTE:
[Ek powerful motivational message in Hinglish — 2-3 lines]

---

Sirf roadmap content do. Koi extra commentary mat add karo.
"""


# ── Generate & Display ────────────────────────────────────────────────────────
if generate_btn:
    if not skill_input.strip():
        st.warning("⚠️ Please enter a skill name to generate your roadmap!")
    else:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])

            with st.spinner("🤖 AI aapka personalized roadmap bana raha hai... Thoda wait karo! ⏳"):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert learning coach. Always respond in Hinglish "
                                "(Hindi + English mix). Be motivating, practical, and structured."
                            ),
                        },
                        {"role": "user", "content": build_prompt(skill_input.strip())},
                    ],
                    temperature=0.75,
                    max_tokens=3500,
                )

            roadmap_text = response.choices[0].message.content

            # ── Display ──
            st.markdown("---")
            st.markdown("## 📋 Aapka 30-Day Roadmap")
            st.markdown(f"<div class='roadmap-text'>{roadmap_text}</div>", unsafe_allow_html=True)

            # ── Tips ──
            st.info(
                "📌 **Tips for Success:**\n\n"
                "✅ Har din kam se kam **1 ghanta** practice karo\n\n"
                "✅ YouTube keywords use karo FREE tutorials ke liye\n\n"
                "✅ Week ke end mein mini project zaroor banao\n\n"
                "✅ Notes banao aur revision karte raho"
            )

            # ── Download ──
            st.markdown("### 💾 Roadmap Save Karo")
            file_name = f"{skill_input.strip().replace(' ', '_')}_30Day_Roadmap.txt"
            st.download_button(
                label="⬇️ Download Roadmap (.txt)",
                data=roadmap_text,
                file_name=file_name,
                mime="text/plain",
                use_container_width=True,
            )

        except KeyError:
            st.error(
                "🔑 **API Key nahi mili!** Streamlit Cloud Secrets mein "
                "`GROQ_API_KEY` add karo. Neeche instructions dekho."
            )
        except Exception as e:
            st.error(f"❌ Kuch gadbad ho gayi: {e}\n\nThodi der baad try karo.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#6b66a8; font-size:0.85rem;'>"
    "🚀 AI Skill Master &nbsp;|&nbsp; Powered by Groq + Streamlit &nbsp;|&nbsp; Made for Indian Students ❤️"
    "</p>",
    unsafe_allow_html=True,
)
