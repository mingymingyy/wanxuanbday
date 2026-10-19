"""
Happy Birthday Streamlit app

Run locally (from inside this folder, so the photos load):
    pip install streamlit
    streamlit run birthday_app.py
"""
import base64
import html
import io
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps

# ==================== EDIT THESE ====================
NAME = "Wan Xuan"
BIRTHDAY = date(2006, 10, 20)
MESSAGE = (
    "Happy birthday needy beta 🥺👉👈 I hope to spend more time hanging out with you and going "
    "for more friendly hangouts 🍜🧋🤪 You are so sweet and always go out of your way to make "
    "others feel loved 🥹💗 so I hope you will experience the same for your birthday 🎂🎉🫶 "
    "I hope you continue being the bubbly and cute girl that you are and stay happy always 🌸😊"
)
SIGN_OFF = "With love, always 💗"

# Photos live in the "photos" folder next to this file.
# Each memory: file name, a handwritten caption, a little sticker label, and where to centre the crop.
PHOTOS_DIR = Path(__file__).parent / "photos"
MEMORIES = [
    {"file": "1.jpg", "caption": "where it all started 🍼", "tag": "then", "focus": "62% 50%"},
    {"file": "2.jpg", "caption": "MRT station photoshoot 🚇", "tag": "now", "focus": "55% 50%"},
    {"file": "3.jpg", "caption": "boat rides & shopping days 🛶", "tag": "now", "focus": "50% 35%"},
    {"file": "4.jpg", "caption": "café catch-ups 🍩", "tag": "now", "focus": "55% 40%"},
]

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

for key, default in {
    "unlocked": False, "attempts": 0, "blown": False, "fire_balloons": False, "letter_open": False,
}.items():
    st.session_state.setdefault(key, default)

# ---------------------------------------------------------------- styling
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400;1,9..144,600&family=DM+Sans:wght@400;500;700&family=Caveat:wght@500;700&display=swap');

:root {
  --ink: #4a2433;
  --ink-soft: #7d5a66;
  --rose: #b4466b;
  --rose-dark: #963858;
  --blush: #f6c9d3;
  --gold: #b88a3e;
  --cream: #fffaf4;
  --line: #ecd6b4;
  --shadow: 0 18px 50px rgba(150, 56, 88, .12);
}

.stApp { font-family: 'DM Sans', sans-serif; color: var(--ink); }
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 15% 10%, rgba(246, 213, 220, .9), transparent 45%),
    radial-gradient(circle at 85% 85%, rgba(242, 223, 196, .8), transparent 45%),
    linear-gradient(170deg, #fffaf4 0%, #fbeeee 55%, #f7e6ec 100%);
  background-attachment: fixed;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMain"] { overflow-x: hidden; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }
.block-container { position: relative; z-index: 2; padding-top: 3rem; padding-bottom: 4rem; max-width: 760px; }

/* ------------ headings */
.eyebrow {
  text-align: center; font-family: 'DM Sans', sans-serif !important; font-size: .82rem !important;
  font-weight: 700; letter-spacing: .32em; text-transform: uppercase; color: var(--gold) !important; margin: 0 0 .4rem;
  animation: rise-in .7s ease both;
}
.title {
  font-family: 'Fraunces', serif !important; font-style: italic; font-weight: 600;
  font-size: clamp(2.4rem, 8vw, 4rem) !important; line-height: 1.12 !important;
  text-align: center; color: var(--rose) !important; margin: 0 0 .5rem; letter-spacing: -.01em;
  animation: rise-in .9s cubic-bezier(.2, .9, .3, 1) both;
}
.title .shimmer {
  background: linear-gradient(100deg, var(--rose) 20%, #e08aa6 40%, var(--gold) 50%, #e08aa6 60%, var(--rose) 80%);
  background-size: 250% 100%; -webkit-background-clip: text; background-clip: text; color: transparent;
  animation: shimmer 6s ease-in-out infinite;
}
@keyframes shimmer { 0%, 100% {background-position: 100% 0} 50% {background-position: 0 0} }
.flourish { text-align: center; color: var(--gold) !important; font-size: 1rem !important; letter-spacing: .6em; margin: 0 0 1rem; }
.pill-row { display: flex; justify-content: center; margin: 0 0 .6rem; }
.pill {
  display: inline-flex; align-items: center; gap: .45rem; padding: .4rem 1rem; border-radius: 999px;
  background: rgba(255, 255, 255, .8); border: 1px solid var(--line); color: var(--rose) !important;
  font-size: .9rem; font-weight: 500; box-shadow: 0 6px 16px rgba(150, 56, 88, .08); animation: rise-in 1s ease both;
}
.pill .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--rose); animation: pulse 1.6s ease-in-out infinite; }
@keyframes pulse { 0%, 100% {transform: scale(1); opacity: 1} 50% {transform: scale(1.6); opacity: .4} }
@keyframes rise-in { 0% {transform: translateY(18px); opacity: 0} 100% {transform: none; opacity: 1} }

.section-head { text-align: center; margin: 2.6rem 0 1rem; }
.section-head .kicker { font-size: .75rem !important; font-weight: 700; letter-spacing: .3em; text-transform: uppercase; color: var(--gold) !important; margin: 0; }
.section-head .section { font-family: 'Fraunces', serif !important; font-style: italic; font-weight: 600; color: var(--rose) !important; font-size: 2rem !important; margin: .1rem 0 0; }
.section-head .sub { color: var(--ink-soft) !important; font-size: .92rem !important; margin: .2rem 0 0; }

/* ------------ lock screen */
[data-testid="stForm"] {
  background: rgba(255, 255, 255, .88); border: 1px solid var(--line); border-radius: 22px;
  padding: 2rem 2rem 1.6rem; box-shadow: var(--shadow); animation: rise-in 1s ease both;
}
.seal {
  width: 64px; height: 64px; margin: -3.4rem auto .8rem; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #d36b8d, var(--rose) 55%, var(--rose-dark));
  box-shadow: 0 6px 16px rgba(150, 56, 88, .35), inset 0 -3px 6px rgba(0, 0, 0, .15);
  display: flex; align-items: center; justify-content: center; font-size: 1.6rem;
}
.lock-note {
  text-align: center; font-family: 'Fraunces', serif !important; font-style: italic;
  font-size: 1.2rem !important; color: var(--ink) !important; margin: 0 0 .2rem;
}
.lock-sub { text-align: center; color: var(--ink-soft) !important; font-size: .9rem !important; margin: 0 0 1rem; }
.stTextInput label p { font-weight: 500; color: var(--ink) !important; font-size: .95rem; }
.stTextInput [data-baseweb="input"] { background: var(--cream) !important; border-radius: 12px; border-color: var(--line) !important; }
.stTextInput input { background: var(--cream) !important; color: var(--ink) !important; font-family: 'DM Sans', sans-serif; text-align: center; letter-spacing: .04em; }

/* ------------ buttons */
[data-testid="stElementContainer"]:has(> .stButton) { align-self: center; }
[data-testid="stForm"] [data-testid="stElementContainer"]:has([data-testid="stFormSubmitButton"]) { align-self: center; }
.stButton, [data-testid="stFormSubmitButton"] { display: flex; justify-content: center; }
.stButton button[kind="primary"], [data-testid="stFormSubmitButton"] button {
  background: var(--rose); color: #fff !important; border: none; border-radius: 999px; padding: .65rem 1.9rem;
  box-shadow: 0 8px 20px rgba(180, 70, 107, .28); transition: transform .15s ease, background .15s ease;
}
.stButton button[kind="primary"] p, [data-testid="stFormSubmitButton"] button p {
  color: #fff !important; font-family: 'DM Sans', sans-serif; font-weight: 700; font-size: 1rem; letter-spacing: .02em;
}
.stButton button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] button:hover {
  background: var(--rose-dark); transform: translateY(-2px); border: none; color: #fff !important;
}
.stButton button[kind="secondary"] {
  background: transparent; border: 1px solid var(--line); border-radius: 999px; padding: .45rem 1.3rem; color: var(--ink-soft) !important;
}
.stButton button[kind="secondary"] p { font-size: .9rem; color: var(--ink-soft) !important; }
.stButton button[kind="secondary"]:hover { border-color: var(--rose); background: rgba(255, 255, 255, .6); }
.stButton button[kind="secondary"]:hover p { color: var(--rose) !important; }

.oops { text-align: center; color: var(--rose) !important; font-weight: 500; margin-top: .6rem; animation: shake .4s ease; }
@keyframes shake { 0%, 100% {transform: none} 25% {transform: translateX(-6px)} 75% {transform: translateX(6px)} }
.hint { text-align: center; color: var(--gold) !important; font-size: .9rem !important; }

/* ------------ drifting confetti */
.confetti { position: fixed; inset: 0; pointer-events: none; z-index: -1; overflow: hidden; }
.confetti div {
  position: absolute; top: -30px; opacity: .55;
  animation-name: drift; animation-timing-function: linear; animation-iteration-count: infinite;
}
@keyframes drift { 0% {transform: translateY(0) rotate(0)} 100% {transform: translateY(115vh) rotate(540deg)} }

/* ------------ cake */
.cake-wrap { display: flex; justify-content: center; margin: 1.4rem 0 .6rem; animation: rise-in 1s ease both; }
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
.sprinkles { position: absolute; inset: 22px 14px 20px; }
.sprinkles i { position: absolute; width: 4px; height: 10px; border-radius: 3px; }
.plate { width: min(340px, 90vw); height: 14px; background: #fff; border-radius: 50%; margin-top: -4px; box-shadow: 0 8px 18px rgba(74, 36, 51, .12); }
.wish { text-align: center; font-family: 'Caveat', cursive !important; color: var(--rose) !important; font-size: 1.6rem !important; margin-top: .4rem; animation: rise-in .6s ease both; }

/* ------------ stats */
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 1.8rem 0 .4rem; }
.stat {
  background: rgba(255, 255, 255, .78); border: 1px solid #f0dcc2; border-radius: 18px; padding: 1rem .8rem;
  text-align: center; animation: rise-in .8s ease both;
}
.stat:nth-child(2) { animation-delay: .1s; } .stat:nth-child(3) { animation-delay: .2s; }
.stat .ico { font-size: 1.2rem; line-height: 1; }
.stat .num { font-family: 'Fraunces', serif; font-size: 1.8rem; font-weight: 600; color: var(--rose); line-height: 1.3; }
.stat .lbl { font-size: .8rem; color: var(--ink-soft); letter-spacing: .02em; }

/* ------------ envelope + letter */
.envelope {
  position: relative; width: min(340px, 86vw); aspect-ratio: 16 / 10; margin: .4rem auto 1.1rem;
  background: linear-gradient(160deg, #fdeee0, #f8dccf); border-radius: 10px; box-shadow: var(--shadow);
  overflow: hidden; animation: float 4s ease-in-out infinite;
}
.envelope::before {
  content: ""; position: absolute; inset: 0;
  background: linear-gradient(to top right, transparent 49.5%, #f3cdbf 50%) left / 50% 100% no-repeat,
              linear-gradient(to top left, transparent 49.5%, #f3cdbf 50%) right / 50% 100% no-repeat;
}
.envelope::after {
  content: ""; position: absolute; left: 0; right: 0; top: 0; height: 58%;
  background: linear-gradient(#f6d5c8, #f1c7b7); clip-path: polygon(0 0, 100% 0, 50% 100%);
  filter: drop-shadow(0 3px 3px rgba(150, 56, 88, .12));
}
.envelope .to {
  position: absolute; left: 0; right: 0; bottom: 5%; text-align: center; z-index: 1;
  font-family: 'Caveat', cursive; font-size: 1.5rem; color: var(--ink);
}
.envelope .wax {
  position: absolute; left: 50%; top: 58%; transform: translate(-50%, -50%); z-index: 2;
  width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
  background: radial-gradient(circle at 35% 30%, #d36b8d, var(--rose) 55%, var(--rose-dark));
  box-shadow: 0 4px 10px rgba(150, 56, 88, .35), inset 0 -3px 6px rgba(0, 0, 0, .15);
}
@keyframes float { 0%, 100% {transform: translateY(0) rotate(-1deg)} 50% {transform: translateY(-6px) rotate(1deg)} }

.letter {
  position: relative; border: 1px solid var(--line); border-radius: 6px; margin: .4rem 0 1rem;
  padding: 2.2rem 2.3rem 2rem; box-shadow: var(--shadow);
  background: radial-gradient(circle at 100% 0, rgba(246, 201, 211, .35), transparent 40%), #fffdf8;
  animation: unfold .9s cubic-bezier(.2, .9, .3, 1) both; transform-origin: top center;
}
.letter::before {
  content: ""; position: absolute; top: -12px; left: 50%; width: 110px; height: 26px; transform: translateX(-50%) rotate(-2deg);
  background: rgba(233, 163, 182, .55); border-radius: 2px;
}
@keyframes unfold { 0% {transform: perspective(900px) rotateX(-70deg); opacity: 0} 100% {transform: none; opacity: 1} }
.letter p { font-family: 'Fraunces', serif !important; color: var(--ink) !important; }
.letter .dear { font-style: italic; font-weight: 600; color: var(--rose) !important; font-size: 1.5rem !important; margin: 0 0 .7rem; }
.letter .body { font-size: 1.18rem !important; line-height: 1.9 !important; margin: 0 0 1rem; }
.letter .sign { font-family: 'Caveat', cursive !important; font-size: 1.7rem !important; color: var(--rose) !important; text-align: right; margin: 1.2rem 0 0; }

/* ------------ memories scrapbook */
.gallery { display: grid; grid-template-columns: repeat(2, 1fr); gap: 34px 26px; margin: .4rem 0 1rem; padding: 10px 6px 0; }
.polaroid {
  position: relative; display: block; background: #fff; padding: 11px 11px 0; border-radius: 4px; text-decoration: none !important;
  box-shadow: 0 12px 28px rgba(74, 36, 51, .18); transition: transform .3s cubic-bezier(.2, .9, .3, 1.3), box-shadow .3s ease;
  animation: drop-in .8s cubic-bezier(.2, .9, .3, 1.2) backwards; cursor: zoom-in;
}
.polaroid:nth-child(1) { --tilt: -3deg; animation-delay: .05s; }
.polaroid:nth-child(2) { --tilt: 2.5deg; animation-delay: .15s; }
.polaroid:nth-child(3) { --tilt: 2deg; animation-delay: .25s; }
.polaroid:nth-child(4) { --tilt: -2.5deg; animation-delay: .35s; }
.polaroid { transform: rotate(var(--tilt, 0deg)); }
@keyframes drop-in { 0% {transform: translateY(-24px) rotate(0) scale(.95); opacity: 0} 100% {transform: rotate(var(--tilt, 0deg)); opacity: 1} }
.polaroid:hover { transform: rotate(0) scale(1.04); box-shadow: 0 22px 44px rgba(74, 36, 51, .26); z-index: 3; }
.polaroid::before {
  content: ""; position: absolute; top: -11px; left: 50%; width: 76px; height: 22px; transform: translateX(-50%) rotate(-3deg);
  background: rgba(226, 196, 140, .6); border-radius: 2px; z-index: 1;
}
.polaroid:nth-child(even)::before { background: rgba(233, 163, 182, .55); transform: translateX(-50%) rotate(4deg); }
.polaroid .frame { position: relative; overflow: hidden; border-radius: 2px; aspect-ratio: 1 / 1; }
.polaroid img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .6s ease; }
.polaroid:hover img { transform: scale(1.05); }
.polaroid .tag {
  position: absolute; top: 10px; right: 10px; padding: .1rem .65rem; border-radius: 999px; z-index: 1;
  background: rgba(255, 250, 244, .92); color: var(--rose); font-size: .72rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase;
}
.polaroid .cap {
  font-family: 'Caveat', cursive !important; color: var(--ink) !important; text-align: center;
  margin: 0; padding: .55rem .2rem .7rem; font-size: 1.45rem !important; line-height: 1.2 !important;
}
.gallery-note { text-align: center; color: var(--ink-soft) !important; font-size: .85rem !important; margin: 0; }

/* click-to-enlarge (pure CSS, uses the URL hash) */
.lightbox {
  position: fixed; inset: 0; z-index: 999999; display: none; align-items: center; justify-content: center;
  background: rgba(40, 18, 28, .82); backdrop-filter: blur(6px); padding: 24px;
}
.lightbox:target { display: flex; animation: fade .25s ease both; }
.lightbox .shot { position: relative; z-index: 1; background: #fff; padding: 12px 12px 0; border-radius: 4px; max-width: min(92vw, 820px); animation: pop .35s cubic-bezier(.2, .9, .3, 1.2) both; }
.lightbox img { display: block; max-width: 100%; max-height: 74vh; border-radius: 2px; }
.lightbox .cap { font-family: 'Caveat', cursive !important; font-size: 1.7rem !important; color: var(--ink) !important; text-align: center; margin: 0; padding: .5rem 0 .7rem; }
.lightbox .backdrop { position: absolute; inset: 0; cursor: zoom-out; }
.lightbox .close {
  position: absolute; top: 16px; right: 20px; z-index: 2; width: 42px; height: 42px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; background: rgba(255, 255, 255, .9);
  color: var(--ink) !important; font-size: 1.3rem; text-decoration: none !important;
}
@keyframes fade { from {opacity: 0} to {opacity: 1} }
@keyframes pop { from {transform: scale(.92); opacity: 0} to {transform: none; opacity: 1} }

/* ------------ closing */
.closing { text-align: center; margin: 2.8rem 0 1.4rem; animation: rise-in 1s ease both; }
.closing .big { font-family: 'Fraunces', serif !important; font-style: italic; font-weight: 600; color: var(--rose) !important; font-size: clamp(1.8rem, 6vw, 2.4rem) !important; margin: 0; }
.closing .small { color: var(--ink-soft) !important; margin: .3rem 0 0; }
.closing .hearts { font-size: 1.3rem; letter-spacing: .4em; margin: .6rem 0 0; }

@media (max-width: 560px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; }
  .gallery { grid-template-columns: 1fr; gap: 36px; padding: 10px 18px 0; }
  .letter { padding: 1.8rem 1.4rem 1.6rem; }
  .letter .body { font-size: 1.08rem !important; }
  .stat .num { font-size: 1.4rem; }
  .stat .lbl { font-size: .72rem; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
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
IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp"}
SPRINKLE_COLOURS = ["#ffffff", "#b4466b", "#d9b26f", "#b9cbb0"]


def sprinkles_html(seed: int) -> str:
    bits = []
    for i in range(9):
        left = (i * 31 + seed * 17) % 94
        top = (i * 23 + seed * 11) % 70
        angle = (i * 47 + seed * 29) % 180
        colour = SPRINKLE_COLOURS[(i + seed) % len(SPRINKLE_COLOURS)]
        bits.append(f'<i style="left:{left}%;top:{top}%;background:{colour};transform:rotate({angle}deg)"></i>')
    return f'<div class="sprinkles">{"".join(bits)}</div>'


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
        f'<div class="tier t1">{sprinkles_html(1)}</div>'
        f'<div class="tier t2">{sprinkles_html(2)}</div>'
        f'<div class="tier t3">{sprinkles_html(3)}</div>'
        '<div class="plate"></div></div></div>'
    )


EMOJI_RUN = re.compile(r"[\U0001F000-\U0001FAFF☀-➿️‍]+")


def keep_emoji_together(text: str) -> str:
    return EMOJI_RUN.sub(lambda m: f'<span style="white-space:nowrap">{m.group(0)}</span>', text)


def jpeg_data_uri(img: Image.Image, max_side: int) -> str:
    img = img.copy()
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


@st.cache_data
def load_memories() -> list[dict]:
    """Small thumbnails for the scrapbook plus a larger copy for the click-to-enlarge view."""
    if not PHOTOS_DIR.is_dir():
        return []
    configured = {m["file"]: m for m in MEMORIES}
    # Configured photos first (in MEMORIES order), then any extra photos dropped into the folder
    extras = sorted(p.name for p in PHOTOS_DIR.iterdir() if p.suffix.lower() in IMAGE_TYPES and p.name not in configured)
    memories = []
    for name in [m["file"] for m in MEMORIES] + extras:
        path = PHOTOS_DIR / name
        if not path.is_file():
            continue
        meta = configured.get(name, {})
        img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        memories.append({
            "thumb": jpeg_data_uri(img, 640),
            "full": jpeg_data_uri(img, 1400),
            "caption": meta.get("caption", ""),
            "tag": meta.get("tag", ""),
            "focus": meta.get("focus", "50% 50%"),
        })
    return memories


def gallery_html(memories: list[dict]) -> str:
    cards, boxes = [], []
    for i, m in enumerate(memories, start=1):
        caption = keep_emoji_together(html.escape(m["caption"]))
        tag = f'<span class="tag">{html.escape(m["tag"])}</span>' if m["tag"] else ""
        cards.append(
            f'<a class="polaroid" href="#memory-{i}" target="_self">'
            f'<div class="frame">{tag}<img src="{m["thumb"]}" alt="{html.escape(m["caption"])}" '
            f'style="object-position:{m["focus"]}"></div>'
            f'<p class="cap">{caption}</p></a>'
        )
        boxes.append(
            f'<div class="lightbox" id="memory-{i}">'
            f'<a class="backdrop" href="#memories" target="_self" aria-label="Close"></a>'
            f'<a class="close" href="#memories" target="_self" aria-label="Close">✕</a>'
            f'<div class="shot"><img src="{m["full"]}" alt="{html.escape(m["caption"])}">'
            f'<p class="cap">{caption}</p></div></div>'
        )
    return f'<div class="gallery" id="memories">{"".join(cards)}</div>{"".join(boxes)}'


def section_head(kicker: str, title: str, sub: str = "") -> None:
    sub_html = f'<p class="sub">{sub}</p>' if sub else ""
    st.markdown(
        f'<div class="section-head"><p class="kicker">{kicker}</p><p class="section">{title}</p>{sub_html}</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------- pages
def login_page() -> None:
    st.markdown(f'<p class="eyebrow">For {html.escape(NAME)}</p>', unsafe_allow_html=True)
    st.markdown('<p class="title">A little something<br>for you</p>', unsafe_allow_html=True)
    st.markdown('<p class="flourish">✦ ✦ ✦</p>', unsafe_allow_html=True)
    st.write("")

    with st.form("lock"):
        st.markdown('<div class="seal">💌</div>', unsafe_allow_html=True)
        st.markdown('<p class="lock-note">Sealed with a very special date</p>', unsafe_allow_html=True)
        st.markdown('<p class="lock-sub">Only one person should know this one 🔒</p>', unsafe_allow_html=True)
        password = st.text_input(
            "Password", type="password", placeholder="DD / MM / YYYY", label_visibility="collapsed"
        )
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
    is_today = (today.month, today.day) == (BIRTHDAY.month, BIRTHDAY.day)

    # ---- hero
    st.markdown(f'<p class="eyebrow">Happy {ordinal(turning)}</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="title">Happy Birthday,<br><span class="shimmer">{html.escape(NAME)}!</span></p>',
        unsafe_allow_html=True,
    )
    if is_today:
        pill = "It's your day today"
    elif before_bday:
        pill = f"{(BIRTHDAY.replace(year=today.year) - today).days} days to go"
    else:
        pill = f"Still celebrating your {ordinal(turning)}"
    st.markdown(
        f'<div class="pill-row"><span class="pill"><span class="dot"></span>{pill}</span></div>',
        unsafe_allow_html=True,
    )

    # ---- cake
    st.markdown(cake_html(turning, st.session_state.blown), unsafe_allow_html=True)
    label = "Light them again 🕯️" if st.session_state.blown else "Make a wish and blow 🌬️"
    if st.button(label, type="primary"):
        st.session_state.blown = not st.session_state.blown
        st.session_state.fire_balloons = st.session_state.blown
        st.rerun()
    if st.session_state.blown:
        st.markdown('<p class="wish">wish made, it\'s on its way ✨</p>', unsafe_allow_html=True)

    days = (today - BIRTHDAY).days
    st.markdown(
        '<div class="stats">'
        f'<div class="stat"><div class="ico">🌍</div><div class="num">{days:,}</div><div class="lbl">days on Earth</div></div>'
        f'<div class="stat"><div class="ico">✨</div><div class="num">{days // 7:,}</div><div class="lbl">weeks of being awesome</div></div>'
        f'<div class="stat"><div class="ico">☀️</div><div class="num">{age_now}</div><div class="lbl">trips around the sun</div></div>'
        "</div>",
        unsafe_allow_html=True,
    )

    # ---- letter
    section_head("A note", "Something for you to read", "")
    if not st.session_state.letter_open:
        st.markdown(
            f'<div class="envelope"><div class="wax">💗</div><div class="to">to {html.escape(NAME)}</div></div>',
            unsafe_allow_html=True,
        )
        if st.button("Open the letter 💌", type="primary"):
            st.session_state.letter_open = True
            st.rerun()
    else:
        st.markdown(
            '<div class="letter">'
            f'<p class="dear">Dear {html.escape(NAME)},</p>'
            + "".join(
                f'<p class="body">{keep_emoji_together(html.escape(para.strip()))}</p>'
                for para in MESSAGE.split("\n\n")
            )
            + f'<p class="sign">{keep_emoji_together(html.escape(SIGN_OFF))}</p></div>',
            unsafe_allow_html=True,
        )

    # ---- memories
    memories = load_memories()
    if memories:
        section_head("Scrapbook", "Memories", "From then till now")
        st.markdown(gallery_html(memories), unsafe_allow_html=True)
        st.markdown('<p class="gallery-note">tap a photo to see it bigger</p>', unsafe_allow_html=True)

    # ---- closing
    st.markdown(
        '<div class="closing">'
        f'<p class="big">Here\'s to {turning}!</p>'
        '<p class="small">May this year be as sweet as you are.</p>'
        '<p class="hearts">💗🎂🥂</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("Lock it again 🔒"):
        st.session_state.unlocked = False
        st.session_state.blown = False
        st.session_state.letter_open = False
        st.session_state.attempts = 0
        st.rerun()


today_local = datetime.now(LOCAL_TZ).date()
if st.session_state.unlocked:
    birthday_page(today_local)
else:
    login_page()
