from khata_parser import parse, is_sure

tests = [
    ("Ramesh ko 2 kilo chawal 120 udhaar", "udhaar", "Ramesh", 120),
    ("aaj 5 kilo aata becha 200 mein", "sale", "", 200),
    ("Ramesh ne 100 rupaye diye", "payment", "Ramesh", 100),
    ("Sita ka 3 packet biscuit 30 udhaar", "udhaar", "Sita", 30),
    ("रमेश को 2 किलो चावल 120 उधार", "udhaar", "रमेश", 120),
    ("सुरेश को 3 किलो चावल का 150 उधार", "udhaar", "सुरेश", 150),
    ("3 किलो चावल का 150", "sale", "", 150),
    ("suresh ko 3 kilo chawal 150 udhaar", "udhaar", "Suresh", 150),
    ("Gave Suresh 3 kg rice 150 on credit", "udhaar", "Suresh", 150),
    ("Sold 5 kg flour for 200", "sale", "", 200),
    ("Suresh paid 100", "payment", "Suresh", 100),
    ("Received 100 from Suresh", "payment", "Suresh", 100),
]
ok = 0
for text, typ, cust, amt in tests:
    e = parse(text)
    good = (e["type"], e["customer"], e["amount"]) == (typ, cust, amt) and is_sure(e)
    ok += good
    print("OK " if good else "BAD", text, e)
print(f"{ok}/{len(tests)} correct")

for text, qty, item in [
    ("Suresh ko teen kilo chawal dedh sau udhaar", "3 kilo", "chawal"),
    ("सुरेश को तीन किलो चावल डेढ़ सौ उधार", "3 किलो", "चावल"),
    ("Suresh ko 3kg chawal 150 udhaar", "3 kg", "chawal"),
    ("Suresh ko aadha kilo chawal 50 udhaar", "0.5 kilo", "chawal"),
]:
    e = parse(text)
    print("OK " if (e["qty"], e["item"]) == (qty, item) else "BAD", text, e)