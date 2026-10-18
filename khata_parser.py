import re, unicodedata

def nfc(s):
    return unicodedata.normalize("NFC", s)

DIG = str.maketrans("०१२३४५६७८९", "0123456789")
NUM = re.compile(r"\d+(\.\d+)?")

# ---- number words (add more here if you see one that is missed) ----
ONES = {nfc(k): v for k, v in {
    "ek": 1, "एक": 1, "one": 1, "do": 2, "दो": 2, "two": 2,
    "teen": 3, "तीन": 3, "three": 3, "char": 4, "chaar": 4, "चार": 4, "four": 4,
    "paanch": 5, "panch": 5, "पांच": 5, "पाँच": 5, "five": 5,
    "chhe": 6, "chhah": 6, "छह": 6, "छः": 6, "six": 6,
    "saat": 7, "सात": 7, "seven": 7, "aath": 8, "आठ": 8, "eight": 8,
    "nau": 9, "नौ": 9, "nine": 9, "das": 10, "दस": 10, "ten": 10,
    "pandrah": 15, "पंद्रह": 15, "fifteen": 15, "bees": 20, "बीस": 20, "twenty": 20,
    "pachees": 25, "pacchis": 25, "पच्चीस": 25, "tees": 30, "तीस": 30, "thirty": 30,
    "chalis": 40, "चालीस": 40, "forty": 40, "pachas": 50, "पचास": 50, "fifty": 50,
    "साठ": 60, "sixty": 60, "pachattar": 75, "पचहत्तर": 75,
    "assi": 80, "अस्सी": 80, "eighty": 80, "nabbe": 90, "नब्बे": 90, "ninety": 90,
}.items()}
FRAC = {nfc(k): v for k, v in {
    "aadha": 0.5, "adha": 0.5, "आधा": 0.5, "half": 0.5,
    "dedh": 1.5, "derh": 1.5, "डेढ़": 1.5, "dhai": 2.5, "ढाई": 2.5,
    "sawa": 1.25, "सवा": 1.25,
}.items()}
MULT = {nfc(k): v for k, v in {
    "sau": 100, "सौ": 100, "hundred": 100,
    "hazaar": 1000, "hazar": 1000, "हज़ार": 1000, "हजार": 1000, "thousand": 1000,
}.items()}

UDHAAR = {"udhaar", "udhar", "uddhar", "उधार", "उधारी", "baaki", "बाकी",
          "credit", "owes", "owe", "due", "borrowed"}
PAID = {"wapas", "vapas", "jama", "chukaya", "chukaye", "diye", "diya",
        "दिए", "दिये", "दिया", "वापस", "जमा", "चुकाया", "चुकाए",
        "paid", "returned", "repaid", "received", "deposited"}
UNITS = {"kilo", "kilos", "kg", "kgs", "kilogram", "kilograms", "किलो", "केजी",
         "किलोग्राम", "कीलो", "packet", "packets", "पैकेट", "litre", "litres",
         "liter", "liters", "लीटर", "dozen", "दर्जन", "gram", "grams", "ग्राम",
         "piece", "pieces", "पीस", "bottle", "bottles", "बोतल"}

STRONG = {"ko", "ne", "se", "को", "ने", "से"}      # NAME comes before these
WEAK = {"ka", "ki", "ke", "का", "की", "के"}
NAME_NEXT = {"to", "from", "gave"}                  # NAME comes after these
NAME_PREV = {"paid", "owes", "owe", "returned", "repaid", "borrowed"}
FILLER = {"of", "ka", "ki", "ke", "का", "की", "के"}
NOT_NAME = (UNITS | UDHAAR | PAID | STRONG | WEAK | NAME_NEXT | NAME_PREV |
            {"aaj", "आज", "kal", "कल", "today", "on", "in", "the", "a", "an",
             "for", "of", "and", "rupaye", "rupees", "rupee", "rs", "रुपये",
             "रुपए", "mein", "में"})


def clean(w):
    return nfc(w).lower().strip(".,।?!")


def normalize_numbers(text):
    """teen kilo -> 3 kilo ; dedh sau -> 150 ; aadha kilo -> 0.5 kilo"""
    words = text.split()
    out, i = [], 0
    while i < len(words):
        x = clean(words[i])
        if x in ONES or x in FRAC or x in MULT:
            total, cur, last_mult, j = 0, None, False, i
            while j < len(words):
                x = clean(words[j])
                if x in MULT:
                    total += (cur if cur is not None else 1) * MULT[x]
                    cur, last_mult = None, True
                elif (x in ONES or x in FRAC) and cur is None and (j == i or last_mult):
                    cur, last_mult = ONES.get(x, FRAC.get(x)), False
                else:
                    break
                j += 1
            out.append(f"{total + (cur or 0):g}")
            i = j
        else:
            out.append(words[i])
            i += 1
    return " ".join(out)


def find_customer(words, low, item):
    def ok(w):
        l = w.lower()
        return l not in NOT_NAME and l != item.lower() and not NUM.fullmatch(w)

    for group in (STRONG, WEAK):
        for i, w in enumerate(low):
            if w in group and i > 0 and ok(words[i - 1]):
                return words[i - 1]
    for i, w in enumerate(low):
        if w in NAME_NEXT and i + 1 < len(words) and ok(words[i + 1]):
            return words[i + 1]
        if w in NAME_PREV and i > 0 and ok(words[i - 1]):
            return words[i - 1]
    return ""


def parse(text):
    t = normalize_numbers(nfc(text)).translate(DIG).replace("₹", " ")
    t = re.sub(r"(?<=\d),(?=\d)", "", t)            # 1,200 -> 1200
    t = re.sub(r"(?<=\d)(?=[^\d\s.,])", " ", t)     # 3kg -> 3 kg
    words = [w.strip(".,।?!") for w in t.split()]
    words = [w for w in words if w]
    low = [nfc(w).lower() for w in words]
    e = {"type": "sale", "customer": "", "item": "", "qty": "", "amount": None}

    if any(w in UDHAAR for w in low):
        e["type"] = "udhaar"
    elif any(w in PAID for w in low):
        e["type"] = "payment"

    nums = [(i, float(w)) for i, w in enumerate(words) if NUM.fullmatch(w)]

    qty_idx, cand = None, ""
    for i, v in nums:
        if i + 1 < len(words) and low[i + 1] in UNITS:
            e["qty"] = f"{v:g} {words[i + 1]}"
            j = i + 2
            while j < len(words) and low[j] in FILLER:
                j += 1
            if j < len(words) and not NUM.fullmatch(words[j]) and low[j] not in NOT_NAME:
                e["item"] = words[j]
            if i > 0 and low[i - 1] not in NOT_NAME and not NUM.fullmatch(words[i - 1]):
                cand = words[i - 1]                  # item said before quantity
            qty_idx = i
            break

    amounts = [v for i, v in nums if i != qty_idx]
    if amounts:
        e["amount"] = amounts[-1]

    e["customer"] = find_customer(words, low, e["item"] or cand).title()
    if not e["item"] and cand and cand.lower() != e["customer"].lower():
        e["item"] = cand
    return e


def is_sure(e):
    if e["amount"] is None:
        return False
    if e["type"] in ("udhaar", "payment") and not e["customer"]:
        return False
    return True