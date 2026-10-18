# Voice Khata

Speak. The ledger writes itself.

Small shopkeepers in India still track credit (udhaar) and sales in a paper khata. It is slow, and typing on a phone is hard when your hands are busy with customers. Voice Khata lets them speak instead. Say an entry in Hindi, Hinglish or English, and the app turns it into a ledger record.

Live app: https://voice-khata.streamlit.app
Demo video: [add link]

## What it does

- Records sales and credit entries by voice
- Works in Hindi, Hinglish and English
- Shows today's credit and today's sales at a glance
- Keeps a full ledger with time, type, customer, item, quantity and amount
- Reads out the day's totals when you tap the summary button

## When speech is unclear

The app does not guess. If it is not sure what it heard, it says so out loud and opens a correction form. You fix the type, customer, item or amount and tap Save. Only then is the entry written to the ledger, so nothing wrong is saved silently.

## Example

Say: "Suresh ko 3 kilo chawal 150 udhaar"

The app records a credit entry for Suresh, rice, 3 kg, Rs 150.

## Built with

- Python and Streamlit
- Gnani speech models for speech to text and text to speech
- pandas for the ledger

## Run it locally

1. Clone the repo and create a virtual environment.
2. Install the packages: `pip install -r requirements.txt`
3. Create a `.env` file with your Gnani API key: `GNANI_API_KEY=your_key_here`
4. Start the app: `streamlit run app.py`

## Project files

- `app.py`: the Streamlit interface
- `gnani.py`: speech to text and text to speech calls
- `khata_parser.py`: turns a transcript into a ledger entry
- `ledger.py`: reads and writes the ledger, builds the summary text
- `test_parser.py`: tests for the parser
- `khata.csv`: demo ledger data

## Note

The live app uses a demo ledger. It can reset when the app restarts, so it is not meant for real shop records yet.

## Next steps

- More Indian languages
- Per-customer balances
- Payment reminders
- A ledger that persists across restarts
