import os, datetime
import pandas as pd

FILE = "khata.csv"
COLS = ["time", "type", "customer", "item", "qty", "amount", "heard"]

TYPE = {
    "hi": {"sale": "बिक्री", "udhaar": "उधार", "payment": "जमा"},
    "hl": {"sale": "Bikri", "udhaar": "Udhaar", "payment": "Jama"},
    "en": {"sale": "Sale", "udhaar": "Credit", "payment": "Payment"},
}
HEAD = {
    "hi": ["समय", "प्रकार", "ग्राहक", "सामान", "मात्रा", "रकम", "सुना"],
    "hl": ["Samay", "Prakar", "Customer", "Saaman", "Matra", "Rakam", "Suna"],
    "en": ["Time", "Type", "Customer", "Item", "Qty", "Amount", "Heard"],
}
SUMMARY = {
    "hi": ("आज की बिक्री {} रुपये", "आज का उधार {} रुपये", "{} का बाकी {} रुपये", "अभी कोई एंट्री नहीं है"),
    "hl": ("Aaj ki bikri {} rupaye", "Aaj ka udhaar {} rupaye", "{} ka baaki {} rupaye", "Abhi koi entry nahi hai"),
    "en": ("Today's sales {} rupees", "Today's credit {} rupees", "{} owes {} rupees", "No entries yet"),
}


def load():
    if not os.path.exists(FILE):
        return pd.DataFrame(columns=COLS)
    return pd.read_csv(FILE).fillna("")


def add(e):
    row = {"time": datetime.datetime.now().isoformat(timespec="seconds"),
           "type": e["type"], "customer": e["customer"], "item": e["item"],
           "qty": e["qty"], "amount": e["amount"], "heard": e.get("heard", "")}
    pd.DataFrame([row]).to_csv(FILE, mode="a", header=not os.path.exists(FILE), index=False)


def show(lang):
    df = load().tail(20).iloc[::-1].copy()
    df["type"] = df["type"].map(TYPE[lang])
    df.columns = HEAD[lang]
    return df


def confirm_text(e, lang="hi"):
    a, c, k = f"{e['amount']:g}", e["customer"], e["type"]
    if lang == "hi":
        return {"udhaar": f"{c}, {a} रुपये उधार लिखा",
                "payment": f"{c} से {a} रुपये मिले",
                "sale": f"{a} रुपये की बिक्री लिखी"}[k]
    if lang == "hl":
        return {"udhaar": f"{c}, {a} rupaye udhaar likha",
                "payment": f"{c} se {a} rupaye mile",
                "sale": f"{a} rupaye ki bikri likhi"}[k]
    return {"udhaar": f"{c}, {a} rupees credit recorded",
            "payment": f"Received {a} rupees from {c}",
            "sale": f"Sale of {a} rupees recorded"}[k]


def summary_text(lang="hi"):
    s_sale, s_udh, s_bal, s_empty = SUMMARY[lang]
    df = load()
    if df.empty:
        return s_empty
    df["amount"] = df["amount"].astype(float)
    today = df[df["time"].str.startswith(datetime.date.today().isoformat())]
    sale = today[today["type"] == "sale"]["amount"].sum()
    udh = today[today["type"] == "udhaar"]["amount"].sum()

    given = df[df["type"] == "udhaar"].groupby("customer")["amount"].sum()
    paid = df[df["type"] == "payment"].groupby("customer")["amount"].sum()
    bal = given.sub(paid, fill_value=0)
    bal = bal[(bal > 0) & (bal.index != "")].sort_values(ascending=False).head(3)

    parts = [s_sale.format(f"{sale:g}"), s_udh.format(f"{udh:g}")]
    parts += [s_bal.format(n, f"{v:g}") for n, v in bal.items()]
    return ". ".join(parts)