# 🎙️ Voice Khata

**A voice-first digital ledger (khata) for small shopkeepers.** Speak in Hindi, Hinglish or English, and Voice Khata writes the entry for you: no typing, no forms.

Built for the **Gnani AI Internship Challenge** using Gnani's speech models.

🔗 **Live app:** https://voice-khata.streamlit.app

---

## Why

Millions of small shopkeepers in India still keep a paper *khata* for sales and *udhaar* (credit). Typing into an app is slow and awkward in a busy shop, and many shopkeepers are more comfortable speaking than typing. Voice Khata lets them just say what happened.

> *"सुरेश को 3 किलो चावल 150 उधार"* → saved as a credit entry for Suresh, ₹150.

## Features

- **Speak to record:** sales, credit (udhaar) and payments received, in Hindi, Hinglish or English
- **Smart parsing:** extracts the customer, item, quantity, amount and entry type from natural speech
- **Safety net for unclear speech:** if the app isn't sure what it heard, it asks you to check and correct the entry in a short form before saving
- **Spoken confirmation:** every saved entry is read back to you
- **End-of-day summary:** today's sales, today's credit, and who owes the most, shown and spoken aloud
- **Live dashboard:** today's credit and cash cards plus a clean transaction table
- **Accounts and privacy:** email sign-up and login; every user sees only their own ledger

## How it works

```
 Mic ──► Gnani Prisma (speech-to-text)
              │
              ▼
        khata_parser.py ──► confident? ── yes ──► save to ledger
              │                                   │
              no                                  ▼
              ▼                         Gnani Timbre (text-to-speech)
      correction form ──► save          reads the confirmation aloud
```

| Layer | Tech |
|---|---|
| UI | Streamlit with custom CSS |
| Speech-to-text | Gnani Vachana **Prisma** |
| Text-to-speech | Gnani Vachana **Timbre** |
| Auth and database | Supabase (Auth + Postgres with Row Level Security) |
| Parsing | Rule-based parser in `khata_parser.py` |

## Project structure

```
app.py            Streamlit UI, login/sign-up, voice flow
gnani.py          Gnani speech-to-text and text-to-speech calls
khata_parser.py   Turns a transcript into a structured ledger entry
ledger.py         Reads and writes entries in Supabase, builds spoken summaries
test_parser.py    Tests for the parser
requirements.txt  Python dependencies
```

## Run it locally

**1. Clone and install**

```bash
git clone https://github.com/surbhi-sg/Voice-Khata.git
cd Voice-Khata
python -m venv venv
venv\Scripts\activate        # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

**2. Set up Supabase** (free tier is enough)

1. Create a project at [supabase.com](https://supabase.com).
2. In *Authentication → Sign In / Providers → Email*, turn **Confirm email** off for easy testing (or leave it on and confirm via email).
3. In the *SQL Editor*, run:

```sql
create table public.entries (
  id bigint generated always as identity primary key,
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  time text not null,
  type text not null,
  customer text default '',
  item text default '',
  qty text default '',
  amount numeric default 0,
  heard text default ''
);

alter table public.entries enable row level security;

create policy "read own rows" on public.entries
  for select to authenticated using (user_id = auth.uid());

create policy "add own rows" on public.entries
  for insert to authenticated with check (user_id = auth.uid());
```

**3. Add your keys**

Create `.streamlit/secrets.toml` (already git-ignored):

```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_KEY = "your-anon-or-publishable-key"   # never the service_role key
GNANI_API_KEY = "your-gnani-api-key"
```

If `gnani.py` reads the Gnani key from the environment, put `GNANI_API_KEY=...` in a `.env` file as well.

**4. Run**

```bash
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push the repo to GitHub.
2. Create the app on [share.streamlit.io](https://share.streamlit.io) and point it at `app.py`.
3. Under *Settings → Secrets*, paste the same three keys as above.

## Privacy and security

- Passwords are handled by Supabase Auth and are never stored by this app.
- **Row Level Security** is enabled, so the database itself only returns rows belonging to the logged-in user.
- Only the public (anon/publishable) Supabase key is used. The `service_role` key is never used or committed.
- API keys live in Streamlit secrets or `.env`, both excluded from Git.
- This is a prototype. The project owner can see stored data in the Supabase dashboard, so don't enter sensitive real-world data into the public demo.

## Roadmap

- Password reset and email verification
- Edit and delete entries
- Per-customer balance view and payment reminders
- Export to Excel or PDF
- More languages (Marathi, Tamil, Bengali and others supported by Gnani)
- Offline-friendly mobile app

## Acknowledgements

- [Gnani.ai](https://gnani.ai) for the Vachana speech APIs (Prisma STT and Timbre TTS)
- [Supabase](https://supabase.com) and [Streamlit](https://streamlit.io)
- Built with help from Claude

## Author

**Surbhi** · [GitHub @surbhi-sg](https://github.com/surbhi-sg)
