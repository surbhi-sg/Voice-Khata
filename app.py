import datetime, hashlib
from html import escape
import pandas as pd
import streamlit as st
from gnani import stt, tts
from khata_parser import parse, is_sure
from ledger import load, add, confirm_text, summary_text, TYPE, HEAD

STT_CODE = {"hi": "hi-IN", "hl": "hi-IN", "en": "en-IN"}
TTS_CODE = {"hi": "hi-IN", "hl": "en-hi-IN-latn", "en": "en-IN"}
PILL = {"sale": "p-green", "udhaar": "p-amber", "payment": "p-slate"}
PILL_TEXT = {"sale": "बिक्री / Sale", "udhaar": "उधार / Credit", "payment": "भुगतान / Payment"}

UI = {
    "hi": dict(cap="बोलिए: “सुरेश को 3 किलो चावल 150 उधार”", heard="सुना", saved="सेव हो गया",
               check="जाँच करें", warn="पक्का नहीं हूँ, जाँच कर सेव करें", f_type="प्रकार",
               f_cust="ग्राहक", f_item="सामान", f_amt="रकम", save="सेव करें",
               sum_btn="आज का हिसाब", table="खाता", say_unsure="पक्का समझ नहीं आया, कृपया जाँच लें",
               hero_t="बोलकर खाता लिखिए", hero_s="माइक दबाइए और बोलिए",
               k_credit="कुल उधार", k_cash="बिक्री", k_today="आज"),
    "hl": dict(cap="Boliye: “Suresh ko 3 kilo chawal 150 udhaar”", heard="Suna", saved="Save ho gaya",
               check="Check karein", warn="Pakka nahi hoon, check karke save karein", f_type="Prakar",
               f_cust="Customer", f_item="Saaman", f_amt="Rakam", save="Save karein",
               sum_btn="Aaj ka hisaab", table="Khata", say_unsure="Pakka samajh nahi aaya, kripya check karein",
               hero_t="Bolkar khata likhiye", hero_s="Mic dabaiye aur boliye",
               k_credit="Kul udhaar", k_cash="Bikri", k_today="Aaj"),
    "en": dict(cap="Say: “Gave Suresh 3 kg rice 150 on credit”", heard="Heard", saved="Saved",
               check="Check", warn="Not sure, please check and save", f_type="Type",
               f_cust="Customer", f_item="Item", f_amt="Amount", save="Save",
               sum_btn="Today’s summary", table="Ledger", say_unsure="I did not understand clearly, please check",
               hero_t="Speak to write your ledger", hero_s="Tap the mic and speak",
               k_credit="Today’s Credit", k_cash="Today’s Cash", k_today="Today"),
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');

/* ---------- base ---------- */
.stApp {background: #F8FAFC;}
.stApp :is(p, label, button, input, select, textarea, th, td, b),
.stApp [class*="vk-"], .stApp [class*="vk-"] *, .stApp .pill, .stApp .tw * {
    font-family: Inter, "Noto Sans Devanagari", "Nirmala UI", sans-serif !important;}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stHeader"] {display: none;}
[data-testid="stMainBlockContainer"], .block-container {max-width: 820px; padding: 0 1.25rem 4rem !important;}

/* ---------- navbar ---------- */
.st-key-nav {position: sticky; top: 0; z-index: 50; margin: 0 -1.25rem 24px; padding: 12px 1.25rem;
    background: rgba(255,255,255,.92); backdrop-filter: blur(10px);
    border-bottom: 1px solid #E2E8F0;}
.st-key-nav [data-testid="stHorizontalBlock"] {flex-wrap: nowrap !important; align-items: center; gap: .5rem;}
.st-key-nav [data-testid="stColumn"] {min-width: 0 !important;}
.st-key-nav [data-testid="stColumn"]:last-child [data-testid="stElementContainer"] {display: flex; justify-content: flex-end;}
.vk-brand {display: flex; align-items: center; gap: 10px; white-space: nowrap;}
.vk-logo {width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center;
    background: linear-gradient(135deg, #10B981, #047857); color: #fff; font-weight: 700; font-size: 1.05rem;
    box-shadow: 0 4px 12px rgba(4,120,87,.35);}
.vk-name {font-size: 1.25rem; font-weight: 700; letter-spacing: -0.02em; color: #0F172A;}
.vk-live {display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 9999px;
    background: #ECFDF5; border: 1px solid #A7F3D0; color: #047857; font-size: .72rem; font-weight: 600; letter-spacing: .04em;}
.vk-live i {width: 7px; height: 7px; border-radius: 50%; background: #10B981; animation: vk-blink 1.6s ease-in-out infinite;}
@keyframes vk-blink {0%,100% {opacity: 1; box-shadow: 0 0 0 0 rgba(16,185,129,.55);} 50% {opacity: .6; box-shadow: 0 0 0 5px rgba(16,185,129,0);}}

/* language selector (segmented control) */
.st-key-nav [data-testid="stButtonGroup"] button {font-size: .82rem; padding: 4px 12px; min-height: 34px; border-radius: 9999px;}
.st-key-nav [data-testid="stBaseButton-segmented_controlActive"],
.st-key-nav button[kind="segmented_controlActive"] {background: #047857 !important; border-color: #047857 !important; color: #fff !important;}

/* phone: stack brand above language selector so they never overlap */
@media (max-width: 640px) {
    .st-key-nav {position: static; margin-bottom: 16px;}
    .st-key-nav [data-testid="stHorizontalBlock"] {flex-wrap: wrap !important; row-gap: 10px;}
    .st-key-nav [data-testid="stColumn"] {flex: 1 1 100% !important; width: 100% !important; min-width: 100% !important;}
    .st-key-nav [data-testid="stColumn"]:last-child [data-testid="stElementContainer"] {justify-content: flex-start;}
    .vk-name {font-size: 1.1rem;}
    .st-key-nav [data-testid="stButtonGroup"] button {font-size: .78rem; padding: 4px 10px;}
}

/* ---------- voice hero ---------- */
.st-key-hero {position: relative; overflow: hidden; align-items: center; text-align: center;
    padding: 30px 20px 26px; border: 1px solid #E2E8F0; border-radius: 22px;
    background: radial-gradient(120% 90% at 50% 0%, #D1FAE5 0%, #ECFDF5 28%, #FFFFFF 70%);
    box-shadow: 0 1px 2px rgba(15,23,42,.05), 0 18px 40px -22px rgba(4,120,87,.35);}
.st-key-hero [data-testid="stMarkdownContainer"] {text-align: center;}
.vk-hero-t {font-size: 1.5rem; font-weight: 700; letter-spacing: -0.01em; line-height: 1.4; color: #0F172A;}
.vk-hero-s {font-size: .98rem; line-height: 1.6; color: #475569; margin-bottom: 4px;}
.vk-eg {display: inline-block; margin-top: 6px; padding: 6px 14px; border-radius: 9999px;
    background: rgba(255,255,255,.85); border: 1px solid #E2E8F0; color: #475569;
    font-size: .88rem; font-style: italic; line-height: 1.6;}

/* the real Streamlit recorder, restyled */
.st-key-hero [data-testid="stAudioInput"] {width: 100%; max-width: 440px; margin: 8px auto 0; min-height: 96px;
    display: flex; align-items: center; padding: 10px 16px; background: #fff; border: 1px solid #A7F3D0;
    border-radius: 9999px; box-shadow: 0 0 0 6px rgba(16,185,129,.08), 0 14px 34px -10px rgba(4,120,87,.35);}
.st-key-hero [data-testid="stAudioInput"] > div {background: transparent !important; border: 0 !important; width: 100%;}
.st-key-hero [data-testid="stAudioInput"] button:first-of-type {
    width: 72px; height: 72px; flex: 0 0 72px; border-radius: 50% !important; border: 0 !important; color: #fff !important;
    background: radial-gradient(circle at 30% 28%, #34D399 0%, #059669 55%, #047857 100%) !important;
    box-shadow: 0 0 0 0 rgba(16,185,129,.5), 0 10px 26px rgba(4,120,87,.5);
    transition: transform .18s ease, box-shadow .18s ease; animation: vk-pulse 2.6s ease-out infinite;}
.st-key-hero [data-testid="stAudioInput"] button:first-of-type svg {width: 30px; height: 30px; fill: currentColor; color: #fff;}
.st-key-hero [data-testid="stAudioInput"] button:first-of-type:hover {
    transform: scale(1.08); animation: none;
    box-shadow: 0 0 0 10px rgba(16,185,129,.18), 0 14px 34px rgba(4,120,87,.6);}
.st-key-hero [data-testid="stAudioInput"] button:first-of-type:active {transform: scale(.97);}
@keyframes vk-pulse {0% {box-shadow: 0 0 0 0 rgba(16,185,129,.45), 0 10px 26px rgba(4,120,87,.5);}
    70% {box-shadow: 0 0 0 16px rgba(16,185,129,0), 0 10px 26px rgba(4,120,87,.5);}
    100% {box-shadow: 0 0 0 0 rgba(16,185,129,0), 0 10px 26px rgba(4,120,87,.5);}}
@media (prefers-reduced-motion: reduce) {.vk-live i, .st-key-hero [data-testid="stAudioInput"] button:first-of-type {animation: none !important;}}
audio {width: 100%; height: 40px;}

/* ---------- KPI cards ---------- */
.vk-kpis {display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 22px 0 6px;}
.vk-kpi {border: 1px solid #E2E8F0; border-radius: 14px; padding: 16px 18px; box-shadow: 0 1px 2px rgba(15,23,42,.05);}
.vk-kpi.amber {background: #FFFBEB;}
.vk-kpi.green {background: #ECFDF5;}
.vk-kpi-top {display: flex; align-items: center; justify-content: space-between; gap: 8px;}
.vk-kpi-l {font-size: .85rem; font-weight: 600; color: #475569; line-height: 1.5;}
.vk-kpi-tag {font-size: .68rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; padding: 2px 8px; border-radius: 9999px; line-height: 1.6;}
.amber .vk-kpi-tag {background: #FEF3C7; color: #92400E;}
.green .vk-kpi-tag {background: #D1FAE5; color: #065F46;}
.vk-kpi-v {font-size: 2rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.3; margin-top: 6px; font-variant-numeric: tabular-nums;}
.amber .vk-kpi-v {color: #78350F;}
.green .vk-kpi-v {color: #064E3B;}
@media (max-width: 480px) {.vk-kpi-v {font-size: 1.5rem;} .vk-kpi {padding: 14px;}}

/* ---------- cards ---------- */
.vk-h2 {font-size: 1.2rem; font-weight: 700; line-height: 1.4; color: #0F172A;}
.vk-card {background: #fff; border: 1px solid #E2E8F0; border-radius: 14px; padding: 16px 18px; margin: 12px 0; box-shadow: 0 1px 2px rgba(15,23,42,.06);}
.vk-label {font-size: .8rem; font-weight: 600; color: #475569;}
.vk-heard {font-size: 1.15rem; line-height: 1.6; border: 1px solid #E2E8F0; background: #F8FAFC; border-radius: 8px; padding: 10px 12px; margin-top: 6px; color: #0F172A;}
.vk-line {display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-top: 12px; color: #0F172A; line-height: 1.6;}
.vk-line .amt {margin-left: auto; font-weight: 700; font-variant-numeric: tabular-nums;}
.mut {color: #475569;}

/* ---------- status pills ---------- */
.pill {display: inline-flex; align-items: center; gap: 6px; padding: 3px 11px; border-radius: 9999px; font-size: .78rem; font-weight: 600; white-space: nowrap; line-height: 1.6;}
.pill::before {content: ""; width: 6px; height: 6px; border-radius: 50%; background: currentColor; opacity: .75;}
.p-green {background: #D1FAE5; color: #065F46;}
.p-amber {background: #FEF3C7; color: #92400E;}
.p-slate {background: #E2E8F0; color: #334155;}

/* ---------- transaction table ---------- */
.stApp .tw {background: #fff; border: 1px solid #E2E8F0; border-radius: 14px; overflow-x: auto; box-shadow: 0 1px 2px rgba(15,23,42,.05), 0 10px 28px -20px rgba(15,23,42,.25);}
.stApp .tw table {width: 100%; min-width: 620px; border-collapse: collapse; margin: 0; border: 0;}
.stApp .tw th {background: #F8FAFC; font-size: .72rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; text-align: left;
    padding: 12px 16px; border: 0; border-bottom: 1px solid #E2E8F0; white-space: nowrap; color: #64748B;}
.stApp .tw td {padding: 14px 16px; font-size: .95rem; border: 0; border-bottom: 1px solid #EEF2F6; color: #0F172A; line-height: 1.5; vertical-align: middle;}
.stApp .tw tbody tr {transition: background .12s ease;}
.stApp .tw tbody tr:hover {background: #F8FAFC;}
.stApp .tw tbody tr:last-child td {border-bottom: 0;}
.stApp .tw .num {text-align: right; font-variant-numeric: tabular-nums;}
.stApp .tw td.num {font-weight: 700; font-size: 1rem;}

/* ---------- buttons, form, recorder shell ---------- */
.stButton > button, .stFormSubmitButton > button {min-height: 44px; border-radius: 10px; font-weight: 600; border: 1px solid #E2E8F0; background: #fff; color: #0F172A; box-shadow: 0 1px 2px rgba(15,23,42,.05); transition: all .15s ease;}
.stButton > button:hover {background: #ECFDF5; border-color: #A7F3D0; color: #047857; transform: translateY(-1px);}
.stFormSubmitButton > button[kind="primaryFormSubmit"] {background: #047857; border-color: #047857; color: #fff;}
.stFormSubmitButton > button[kind="primaryFormSubmit"]:hover {background: #065F46; color: #fff;}
[data-testid="stForm"] {border: 1px solid #E2E8F0; border-radius: 14px; background: #fff;}
</style>
"""


def money(v):
    return "₹" + f"{float(v):,.2f}".rstrip("0").rstrip(".")


def today_totals():
    """(credit given today, sales today) taken from the saved ledger."""
    df = load()
    if df is None or df.empty:
        return 0, 0
    d = df.copy()
    d["_d"] = pd.to_datetime(d["time"], errors="coerce").dt.date
    d["_a"] = pd.to_numeric(d["amount"], errors="coerce").fillna(0)
    d = d[d["_d"] == datetime.date.today()]
    return (d.loc[d["type"] == "udhaar", "_a"].sum(),
            d.loc[d["type"] == "sale", "_a"].sum())


def kpi_html(u):
    credit, cash = today_totals()
    return (f'<div class="vk-kpis">'
            f'<div class="vk-kpi amber"><div class="vk-kpi-top"><span class="vk-kpi-l">{u["k_credit"]}</span>'
            f'<span class="vk-kpi-tag">{u["k_today"]}</span></div><div class="vk-kpi-v">{money(credit)}</div></div>'
            f'<div class="vk-kpi green"><div class="vk-kpi-top"><span class="vk-kpi-l">{u["k_cash"]}</span>'
            f'<span class="vk-kpi-tag">{u["k_today"]}</span></div><div class="vk-kpi-v">{money(cash)}</div></div>'
            f'</div>')


def heard_card(text, e, pending, u, lang):
    status = (f'<span class="pill p-amber">{u["check"]}</span>' if pending
              else f'<span class="pill p-green">{u["saved"]}</span>')
    detail = " · ".join(x for x in (e["item"], e["qty"]) if x)
    amount = money(e["amount"]) if e["amount"] is not None else "—"
    return (f'<div class="vk-card"><div style="display:flex;justify-content:space-between;align-items:center">'
            f'<div class="vk-label">{u["heard"]}</div>{status}</div>'
            f'<div class="vk-heard">{escape(text)}</div>'
            f'<div class="vk-line"><span class="pill {PILL[e["type"]]}">{PILL_TEXT[e["type"]]}</span>'
            f'<b>{escape(e["customer"]) or "—"}</b><span class="mut">{escape(detail)}</span>'
            f'<span class="amt">{amount}</span></div></div>')


def ledger_html(lang):
    df = load().tail(20).iloc[::-1]
    cls = ["", "", "", "", "", ' class="num"']
    head = "".join(f"<th{c}>{h}</th>" for c, h in zip(cls, HEAD[lang][:6]))
    rows = ""
    for r in df.itertuples():
        when = datetime.datetime.fromisoformat(r.time).strftime("%d %b, %H:%M")
        rows += (f'<tr><td class="mut" style="white-space:nowrap">{when}</td>'
                 f'<td><span class="pill {PILL[r.type]}">{PILL_TEXT[r.type]}</span></td>'
                 f'<td>{escape(str(r.customer)) or "—"}</td><td>{escape(str(r.item)) or "—"}</td>'
                 f'<td>{escape(str(r.qty)) or "—"}</td><td class="num">{money(r.amount)}</td></tr>')
    if not rows:
        rows = '<tr><td colspan="6" class="mut" style="text-align:center;padding:28px">—</td></tr>'
    return f'<div class="tw"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'


def speak(make_text, lang):
    try:
        return tts(make_text(lang), TTS_CODE[lang])
    except Exception:                       # voice can't do this language: use Hindi
        return tts(make_text("hi"), "hi-IN")


st.set_page_config(page_title="Voice Khata", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)

# ---------- navbar: brand + live tag on the left, language on the right ----------
with st.container(key="nav"):
    nav_l, nav_r = st.columns([3, 2], vertical_alignment="center")
    nav_l.markdown('<div class="vk-brand"><span class="vk-logo">₹</span>'
                   '<span class="vk-name">Voice Khata</span>'
                   '<span class="vk-live"><i></i>LIVE</span></div>', unsafe_allow_html=True)
    with nav_r:
        choice = st.segmented_control("Language", ["हिंदी", "Hinglish", "English"], default="हिंदी",
                                      label_visibility="collapsed") or "हिंदी"
lang = {"हिंदी": "hi", "Hinglish": "hl", "English": "en"}[choice]
u = UI[lang]

# ---------- voice hero ----------
with st.container(key="hero"):
    st.markdown(f'<div class="vk-hero-t">{u["hero_t"]}</div><div class="vk-hero-s">{u["hero_s"]}</div>',
                unsafe_allow_html=True)
    audio = st.audio_input("Record", label_visibility="collapsed")
    st.markdown(f'<div class="vk-eg">{u["cap"]}</div>', unsafe_allow_html=True)

if audio:
    data = audio.getvalue()
    h = hashlib.md5(data).hexdigest()
    if st.session_state.get("last") != h:          # process each recording once
        st.session_state.last = h
        try:
            text = stt(data, STT_CODE[lang])
            e = parse(text)
            e["heard"] = text
            st.session_state.text, st.session_state.entry = text, e
            if is_sure(e):
                add(e)
                st.session_state.pending = False
                st.session_state.say = speak(lambda l: confirm_text(e, l), lang)
            else:
                st.session_state.pending = True
                st.session_state.say = speak(lambda l: UI[l]["say_unsure"], lang)
        except Exception as ex:
            st.error(f"Error: {ex}")

if "text" in st.session_state:
    st.markdown(heard_card(st.session_state.text, st.session_state.entry,
                           st.session_state.get("pending"), u, lang), unsafe_allow_html=True)

if st.session_state.get("pending"):
    e = st.session_state.entry
    st.warning(u["warn"])
    kinds = ["sale", "udhaar", "payment"]
    with st.form("fix"):
        c1, c2 = st.columns(2)
        typ = c1.selectbox(u["f_type"], kinds, index=kinds.index(e["type"]),
                           format_func=lambda k: TYPE[lang][k])
        amt = c2.number_input(u["f_amt"], value=float(e["amount"] or 0))
        cust = c1.text_input(u["f_cust"], e["customer"])
        item = c2.text_input(u["f_item"], e["item"])
        if st.form_submit_button(u["save"], type="primary") and amt > 0:
            fixed = {**e, "type": typ, "customer": cust, "item": item, "amount": amt}
            add(fixed)
            st.session_state.entry = fixed
            st.session_state.pending = False
            st.session_state.say = speak(lambda l: confirm_text(fixed, l), lang)
            st.rerun()

say = st.session_state.pop("say", None)
if say:
    st.audio(say, format="audio/wav", autoplay=True)

# ---------- KPI cards (computed after any new entry is saved) ----------
st.markdown(kpi_html(u), unsafe_allow_html=True)

# ---------- ledger ----------
st.write("")
c1, c2 = st.columns([3, 2], vertical_alignment="center")
c1.markdown(f'<div class="vk-h2">{u["table"]}</div>', unsafe_allow_html=True)
show_sum = c2.button(u["sum_btn"], use_container_width=True)

if show_sum:
    s = summary_text(lang)
    st.markdown(f'<div class="vk-card" style="font-size:1.1rem;font-weight:500">{escape(s)}</div>',
                unsafe_allow_html=True)
    st.audio(speak(lambda l: summary_text(l), lang), format="audio/wav", autoplay=True)

st.markdown(ledger_html(lang), unsafe_allow_html=True)