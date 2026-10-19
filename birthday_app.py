"""
Happy Birthday Streamlit app

Run locally (from inside this folder, so the photos load):
    pip install streamlit
    streamlit run birthday_app.py
"""
import base64
import html
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import streamlit as st

# ==================== EDIT THESE ====================
NAME = "Wan Xuan"
BIRTHDAY = date(2006, 10, 20)
MESSAGE = (
    "Happy birthday needy beta 🥺👉👈 I hope to spend more time hanging out with you and going "
    "for more friendly hangouts 🍜🧋🤪 You are so sweet and always go out of your way to make "
    "others feel loved 🥹💗 so I hope you will experience the same for your birthday 🎂🎉🫶"
)
# Photos live in the "photos" folder next to this file, shown in filename order (1.jpg, 2.jpg, ...)
PHOTOS_DIR = Path(__file__).parent / "photos"
# Optional captions under each polaroid, keyed by filename, e.g. {"1.jpg": "mini Wan Xuan"}
CAPTIONS = {}

# Any of these unlock the page (spaces, slashes, dashes, dots and capitals are ignored)
ACCEPTED_PASSWORDS = [
    "20 October 2006", "20 Oct 2006", "20th October 2006", "October 20 2006",
    "20/10/2006", "20-10-2006", "20.10.2006", "20102006", "20/10/06", "2006-10-20",
]
# ====================================================

LOCAL_TZ = timezone(timedelta(hours=8))  # used only to work out today's date for the age


def normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


ACCEPTED = {normalise(p) for p in ACCEPTED_PASSWORDS}


def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


st.set_page_config(page_title=f"Happy Birthday, {NAME}!", page_icon="🎂", layout="centered")

for key, default in {"unlocked": False, "attempts": 0, "blown": False, "fire_balloons": False}.items():
    st.session_state.setdefault(key, default)

# ---------------------------------------------------------------- styling
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400;1,9..144,600&family=DM+Sans:wght@400;500;700&display=swap');

:root {
  --ink: #4a2433;
  --rose: #b4466b;
  --rose-dark: #963858;
  --gold: #b88a3e;
  --cream: #fffaf4;
}

.stApp { font-family: 'DM Sans', sans-serif; color: var(--ink); }
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 15% 10%, rgba(246, 213, 220, .9), transparent 45%),
    radial-gradient(circle at 85% 85%, rgba(242, 223, 196, .8), transparent 45%),
    linear-gradient(170deg, #fffaf4 0%, #fbeeee 55%, #f7e6ec 100%);
}
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
.block-container { position: relative; z-index: 2; padding-top: 3rem; max-width: 760px; }

.eyebrow {
  text-align: center; font-family: 'DM Sans', sans-serif !important; font-size: .82rem !important;
  font-weight: 700; letter-spacing: .32em; text-transform: uppercase; color: var(--gold) !important; margin: 0 0 .4rem;
}
.title {
  font-family: 'Fraunces', serif !important; font-style: italic; font-weight: 600;
  font-size: clamp(2.4rem, 8vw, 4rem) !important; line-height: 1.12 !important;
  text-align: center; color: var(--rose) !important; margin: 0 0 .5rem; letter-spacing: -.01em;
  animation: rise-in .9s cubic-bezier(.2, .9, .3, 1) both;
}
.flourish { text-align: center; color: var(--gold) !important; font-size: 1rem !important; letter-spacing: .6em; margin: 0 0 1.2rem; }
@keyframes rise-in { 0% {transform: translateY(18px); opacity: 0} 100% {transform: none; opacity: 1} }

/* lock screen */
[data-testid="stForm"] {
  background: rgba(255, 255, 255, .88); border: 1px solid #ecd6b4; border-radius: 22px;
  padding: 2rem 2rem 1.6rem; box-shadow: 0 18px 50px rgba(150, 56, 88, .12);
}
.lock-note {
  text-align: center; font-family: 'Fraunces', serif !important; font-style: italic;
  font-size: 1.15rem !important; color: var(--ink) !important; margin: 0 0 .8rem;
}
.stTextInput label p { font-weight: 500; color: var(--ink) !important; font-size: .95rem; }
.stTextInput [data-baseweb="input"] { background: var(--cream) !important; border-radius: 12px; border-color: #ecd6b4 !important; }
.stTextInput input { background: var(--cream) !important; color: var(--ink) !important; font-family: 'DM Sans', sans-serif; }

[data-testid="stElementContainer"]:has(> .stButton) { align-self: center; }
[data-testid="stForm"] [data-testid="stElementContainer"]:has([data-testid="stFormSubmitButton"]) { align-self: center; }
.stButton, [data-testid="stFormSubmitButton"] { display: flex; justify-content: center; }
.stButton button, [data-testid="stFormSubmitButton"] button {
  background: var(--rose); color: #fff !important; border: none; border-radius: 999px; padding: .65rem 1.9rem;
  box-shadow: 0 8px 20px rgba(180, 70, 107, .28); transition: transform .15s ease, background .15s ease;
}
.stButton button p, [data-testid="stFormSubmitButton"] button p {
  color: #fff !important; font-family: 'DM Sans', sans-serif; font-weight: 700; font-size: 1rem; letter-spacing: .02em;
}
.stButton button:hover, [data-testid="stFormSubmitButton"] button:hover { background: var(--rose-dark); transform: translateY(-2px); border: none; color: #fff !important; }

.oops { text-align: center; color: var(--rose) !important; font-weight: 500; margin-top: .6rem; }
.hint { text-align: center; color: var(--gold) !important; font-size: .9rem !important; }

/* drifting confetti */
.confetti { position: fixed; inset: 0; pointer-events: none; z-index: -1; overflow: hidden; }
.confetti div {
  position: absolute; top: -30px; opacity: .55;
  animation-name: drift; animation-timing-function: linear; animation-iteration-count: infinite;
}
@keyframes drift { 0% {transform: translateY(0) rotate(0)} 100% {transform: translateY(115vh) rotate(540deg)} }

/* cake */
.cake-wrap { display: flex; justify-content: center; margin: 1.4rem 0 .6rem; }
.cake { display: flex; flex-direction: column; align-items: center; }
.candles { display: flex; gap: 12px; align-items: flex-end; margin-bottom: -6px; z-index: 2; }
.numcandle { display: flex; flex-direction: column; align-items: center; }
.numcandle span {
  font-family: 'Fraunces', serif; font-weight: 600; font-size: 4.2rem; line-height: 1;
  background: repeating-linear-gradient(45deg, #e9a3b6 0 7px, #fff6f0 7px 14px);
  -webkit-background-clip: text; background-clip: text; color: transparent; -webkit-text-stroke: 1.5px var(--rose);
}
.flame-slot { height: 30px; display: flex; align-items: flex-end; }
.flame {
  width: 15px; height: 25px; transform-origin: 50% 90%;
  background: radial-gradient(ellipse at 50% 70%, #fff8d6 0%, #ffd56b 40%, #f39a3d 75%, rgba(243, 120, 40, 0) 100%);
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  filter: drop-shadow(0 0 9px #ffcc66); animation: flicker .14s ease-in-out infinite alternate;
}
@keyframes flicker { 0% {transform: scaleY(1) rotate(-2deg)} 100% {transform: scaleY(1.1) rotate(2deg)} }
.smoke { width: 10px; height: 24px; border-radius: 50%; background: rgba(150, 140, 140, .5); filter: blur(3px); animation: smoke 2s ease-out infinite; }
@keyframes smoke { 0% {transform: translateY(6px) scale(.6); opacity: .8} 100% {transform: translateY(-18px) scale(1.4); opacity: 0} }
.wick { width: 2px; height: 10px; background: #5a4334; border-radius: 2px; }
.tier { position: relative; border-radius: 12px 12px 8px 8px; }
.tier.t1 { width: min(170px, 46vw); height: 56px; background: #f6c9d3; }
.tier.t2 { width: min(230px, 62vw); height: 64px; background: #fdeee0; }
.tier.t3 { width: min(290px, 78vw); height: 74px; background: #e9a3b6; }
.tier::before {
  content: ""; position: absolute; top: 0; left: 0; right: 0; height: 18px; border-radius: 12px 12px 0 0;
  background: linear-gradient(#fffaf4, #fffaf4) 0 0 / 100% 6px no-repeat,
              radial-gradient(circle at 10px 0, #fffaf4 10px, transparent 11px) 0 0 / 20px 18px repeat-x;
}
.tier::after { content: ""; position: absolute; left: 0; right: 0; bottom: 14px; height: 3px; background: rgba(184, 138, 62, .55); }
.plate { width: min(340px, 90vw); height: 14px; background: #fff; border-radius: 50%; margin-top: -4px; box-shadow: 0 8px 18px rgba(74, 36, 51, .12); }
.wish { text-align: center; font-family: 'Fraunces', serif !important; font-style: italic; color: var(--rose) !important; font-size: 1.1rem !important; margin-top: .5rem; animation: rise-in .6s ease both; }

/* stats */
.stats { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin: 1.6rem 0; }
.stat { background: rgba(255, 255, 255, .78); border: 1px solid #f0dcc2; border-radius: 18px; padding: .9rem 1.3rem; min-width: 150px; text-align: center; animation: rise-in .8s ease both; }
.stat .num { font-family: 'Fraunces', serif; font-size: 1.8rem; font-weight: 600; color: var(--rose); }
.stat .lbl { font-size: .82rem; color: #7d5a66; letter-spacing: .02em; }

/* message (one font throughout) */
.card {
  position: relative; background: rgba(255, 255, 255, .9); border: 1px solid #ecd6b4; border-radius: 22px;
  padding: 2rem 2.1rem 2.1rem; margin: 1rem 0 1.6rem; box-shadow: 0 18px 50px rgba(150, 56, 88, .12); animation: rise-in .9s ease both;
}
.card, .card p { font-family: 'Fraunces', serif !important; color: var(--ink) !important; }
.card .card-title { font-style: italic; font-weight: 600; color: var(--rose) !important; font-size: 1.55rem !important; margin: 0 0 .8rem; }
.card-body { font-size: 1.2rem !important; line-height: 1.85 !important; margin: 0; }

.section { font-family: 'Fraunces', serif !important; font-style: italic; font-weight: 600; color: var(--rose) !important; font-size: 1.8rem !important; text-align: center; margin: 1.2rem 0 .6rem; }

/* polaroids */
.gallery { display: grid; grid-template-columns: repeat(2, 1fr); gap: 28px 22px; margin: .8rem 0 1.6rem; padding: 0 6px; animation: rise-in .9s ease both; }
.polaroid {
  position: relative; background: #fff; padding: 10px 10px 14px; border-radius: 4px;
  box-shadow: 0 12px 28px rgba(74, 36, 51, .18); transition: transform .25s ease, box-shadow .25s ease;
}
.polaroid:nth-child(4n+1) { transform: rotate(-3deg); }
.polaroid:nth-child(4n+2) { transform: rotate(2.5deg); }
.polaroid:nth-child(4n+3) { transform: rotate(2deg); }
.polaroid:nth-child(4n) { transform: rotate(-2.5deg); }
.polaroid:hover { transform: rotate(0) scale(1.05); box-shadow: 0 18px 38px rgba(74, 36, 51, .26); z-index: 3; }
.polaroid::before {
  content: ""; position: absolute; top: -10px; left: 50%; width: 70px; height: 22px; transform: translateX(-50%) rotate(-3deg);
  background: rgba(226, 196, 140, .6); border-radius: 2px;
}
.polaroid img { width: 100%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 2px; display: block; }
.polaroid .cap { font-family: 'Fraunces', serif !important; font-style: italic; color: var(--ink) !important; text-align: center; margin: 8px 0 0; font-size: 1.05rem !important; min-height: 1.2rem; }
@media (max-width: 520px) { .gallery { grid-template-columns: 1fr; } .card { padding: 1.5rem 1.4rem; } }
</style>
"""

CONFETTI_COLOURS = ["#e9a3b6", "#d9b26f", "#f3cfc2", "#c98aa6", "#e6c98f", "#b9cbb0"]


def confetti_html() -> str:
    parts = ['<div class="confetti">']
    for i in range(26):
        left = (i * 37 + 3) % 98
        w = 6 + (i * 5) % 5
        h = w if i % 3 == 0 else w + 6
        radius = "50%" if i % 3 == 0 else "2px"
        dur = 13 + (i * 7) % 11
        delay = -((i * 4.3) % dur)
        colour = CONFETTI_COLOURS[i % len(CONFETTI_COLOURS)]
        parts.append(
            f'<div style="left:{left}%;width:{w}px;height:{h}px;background:{colour};border-radius:{radius};'
            f'animation-duration:{dur}s;animation-delay:{delay:.1f}s;"></div>'
        )
    parts.append("</div>")
    return "".join(parts)


st.markdown(CSS, unsafe_allow_html=True)
st.markdown(confetti_html(), unsafe_allow_html=True)

# ---------------------------------------------------------------- helpers
IMAGE_TYPES = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png", ".gif": "gif", ".webp": "webp"}


def cake_html(age: int, blown: bool) -> str:
    candles = []
    for digit in str(age):
        top = '<div class="smoke"></div>' if blown else '<div class="flame"></div>'
        candles.append(
            f'<div class="numcandle"><div class="flame-slot">{top}</div>'
            f'<div class="wick"></div><span>{digit}</span></div>'
        )
    return (
        '<div class="cake-wrap"><div class="cake">'
        f'<div class="candles">{"".join(candles)}</div>'
        '<div class="tier t1"></div><div class="tier t2"></div><div class="tier t3"></div>'
        '<div class="plate"></div></div></div>'
    )


EMOJI_RUN = re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]+")


def keep_emoji_together(text: str) -> str:
    return EMOJI_RUN.sub(lambda m: f'<span style="white-space:nowrap">{m.group(0)}</span>', text)


@st.cache_data
def gallery_html() -> str:
    if not PHOTOS_DIR.is_dir():
        return ""
    photos = sorted(p for p in PHOTOS_DIR.iterdir() if p.suffix.lower() in IMAGE_TYPES)
    cards = []
    for photo in photos:
        data = base64.b64encode(photo.read_bytes()).decode()
        caption = html.escape(CAPTIONS.get(photo.name, ""))
        cards.append(
            f'<div class="polaroid"><img src="data:image/{IMAGE_TYPES[photo.suffix.lower()]};base64,{data}" alt="">'
            f'<p class="cap">{caption}</p></div>'
        )
    return f'<div class="gallery">{"".join(cards)}</div>' if cards else ""


# ---------------------------------------------------------------- pages
def login_page() -> None:
    st.markdown(f'<p class="eyebrow">For {html.escape(NAME)}</p>', unsafe_allow_html=True)
    st.markdown('<p class="title">A little something for you</p>', unsafe_allow_html=True)
    st.markdown('<p class="flourish">✦ ✦ ✦</p>', unsafe_allow_html=True)

    with st.form("lock"):
        st.markdown('<p class="lock-note">It\'s locked with a very special date 🔒</p>', unsafe_allow_html=True)
        password = st.text_input("Password", type="password", placeholder="Enter the date")
        submitted = st.form_submit_button("Open it 🎁")

    if submitted:
        if normalise(password) in ACCEPTED:
            st.session_state.unlocked = True
            st.session_state.fire_balloons = True
            st.rerun()
        else:
            st.session_state.attempts += 1
            st.markdown('<p class="oops">Not quite, try again 🙈</p>', unsafe_allow_html=True)
            if st.session_state.attempts >= 3:
                st.markdown(
                    '<p class="hint">Psst... it\'s your birthday. Any format works, like 20/10/2006.</p>',
                    unsafe_allow_html=True,
                )


def birthday_page(today: date) -> None:
    if st.session_state.fire_balloons:
        st.balloons()
        st.session_state.fire_balloons = False

    before_bday = (today.month, today.day) < (BIRTHDAY.month, BIRTHDAY.day)
    age_now = today.year - BIRTHDAY.year - (1 if before_bday else 0)
    turning = age_now + 1 if before_bday else age_now

    st.markdown(f'<p class="eyebrow">Happy {ordinal(turning)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="title">Happy Birthday,<br>{html.escape(NAME)}!</p>', unsafe_allow_html=True)
    st.markdown('<p class="flourish">✦ ✦ ✦</p>', unsafe_allow_html=True)

    st.markdown(cake_html(turning, st.session_state.blown), unsafe_allow_html=True)
    label = "🕯️ Light them again" if st.session_state.blown else "🌬️ Make a wish and blow"
    if st.button(label):
        st.session_state.blown = not st.session_state.blown
        st.session_state.fire_balloons = st.session_state.blown
        st.rerun()
    if st.session_state.blown:
        st.markdown('<p class="wish">Wish made, it\'s on its way ✨</p>', unsafe_allow_html=True)

    days = (today - BIRTHDAY).days
    st.markdown(
        '<div class="stats">'
        f'<div class="stat"><div class="num">{days:,}</div><div class="lbl">days on Earth</div></div>'
        f'<div class="stat"><div class="num">{days // 7:,}</div><div class="lbl">weeks of being awesome</div></div>'
        f'<div class="stat"><div class="num">{age_now}</div><div class="lbl">trips around the sun</div></div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="card"><p class="card-title">A note for you 💌</p>'
        f'<p class="card-body">{keep_emoji_together(html.escape(MESSAGE))}</p></div>',
        unsafe_allow_html=True,
    )

    gallery = gallery_html()
    if gallery:
        st.markdown('<p class="section">Memories</p>', unsafe_allow_html=True)
        st.markdown(gallery, unsafe_allow_html=True)

    st.write("")
    if st.button("🔒 Lock again"):
        st.session_state.unlocked = False
        st.session_state.blown = False
        st.session_state.attempts = 0
        st.rerun()


today_local = datetime.now(LOCAL_TZ).date()
if st.session_state.unlocked:
    birthday_page(today_local)
else:
    login_page()
