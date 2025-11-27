🚨 Day 6 – Fraud Alert Voice Agent (LiveKit + SQLite + Murf Falcon)

This project implements a fully functional Fraud Alert Voice Agent for a fictional bank SecureBank, built as part of the Murf AI Voice Agent Challenge – Day 6.

The agent automatically:

Loads a fraud case from an SQLite database

Greets the customer professionally

Performs safe verification (no sensitive data)

Reads suspicious transaction details

Asks whether the transaction was actually made

Updates the database as confirmed_safe or confirmed_fraud

Ends the call with a calm, reassuring message

Everything runs inside a LiveKit voice session using:

Deepgram → Speech-to-Text

Google Gemini Flash → LLM

Murf Falcon → TTS

SQLite → Fraud Case Storage

This project demonstrates a complete, realistic fraud-alert call flow — safe, fast, and entirely powered by voice AI.

🧠 Features
✅ Primary Goal (MVP)

Loads a fraud case using load_case(user_name)

Asks verification question stored in DB

Verifies customer via verify_answer()

Reads out suspicious details (merchant, card ending, timestamp, amount, etc.)

Asks: “Did you make this transaction?”

Updates case status using update_case_status()

Writes back status + notes into SQLite

Uses no sensitive data (PIN, full card number, password, etc.)

🗄 Database

SQLite table:

CREATE TABLE fraud_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    security_identifier TEXT,
    card_ending TEXT,
    amount TEXT,
    merchant TEXT,
    timestamp TEXT,
    category TEXT,
    source TEXT,
    verification_question TEXT,
    verification_answer TEXT,
    status TEXT,
    notes TEXT,
    updated_at TEXT
);


Includes 5 fully fake sample fraud cases.

📁 Project Structure
backend/
│── src/
│   ├── agent.py          # Fraud Agent (LiveKit voice agent)
│   ├── fraud_tools.py    # SQLite tools (load case, verify, update)
│── shared-data/
│   ├── fraud_cases.db    # SQLite database
│── init_db.py             # Script to initialize sample fraud cases
│── README.md

🚀 How It Works (Call Flow)

Agent:
“Hello, this is SecureBank’s fraud prevention department. May I confirm your name?”

User gives name → tool load_case(name) loads case.

Agent:
“For verification: What is your favorite color?”

User answers → verify_answer(name, answer) returns verified=True/False.

If verified:

Agent reads suspicious transaction details from DB.

Asks: “Did you make this transaction?”

User replies:

YES → mark case as confirmed_safe

NO → mark case as confirmed_fraud

Agent ends politely:
“Thank you. Your case has been updated. Have a safe day.”

🛠 How to Run
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Initialize SQLite DB
python src/init_db.py


You should see:

SQLite database initialized with 5 sample cases!

3️⃣ Start the LiveKit Worker
python src/agent.py


Open the Voice Agent UI in browser → connect → begin the fraud alert flow.

🗣 Voice Tech Used
Component	Provider	Purpose
STT	Deepgram Nova-3	Convert user speech → text
LLM	Google Gemini 2.5 Flash	Smart call flow + reasoning
TTS	Murf Falcon Voices	Natural, crisp, real-time voice
DB	SQLite	Fraud case storage
🔒 Safety Notes

All data is fake

No real card info

No PIN/password handling

Verification uses harmless questions only

Designed strictly for demo/learning purposes

🔗 Command to Push Code to GitHub
git add .
git commit -m "Day 6 – Fraud Alert Voice Agent complete (SQLite + Murf + LiveKit)"
git branch -M main
git remote add origin https://github.com/YOURUSERNAME/YOUR-REPO.git
git push -u origin main


Replace with your repo URL.

🎉 LinkedIn Post (Copy-Paste Ready)

🚨 Day 6 of the Murf AI Voice Agent Challenge – Fraud Alert Voice Agent!

Today I built a fully functional Fraud Alert Voice Agent for a fictional bank using:

🔹 LiveKit for real-time voice interaction
🔹 Deepgram Nova STT for accurate speech recognition
🔹 Google Gemini Flash for reasoning + conversational flow
🔹 Murf Falcon TTS for natural, crisp responses
🔹 SQLite as a fraud-case database

🧠 The agent can:
✔ Verify the user (safe, non-sensitive check)
✔ Read a suspicious transaction from the database
✔ Ask if the user actually made the purchase
✔ Classify the case as confirmed_safe or confirmed_fraud
✔ Write the results back into SQLite
✔ Speak professionally and calmly like a real bank fraud analyst

This was one of the most realistic agent flows so far — felt like building an actual fraud-prevention hotline!

Excited for the upcoming days 🔥

#MurfAIVoiceAgentsChallenge #10DaysofAIVoiceAgents #MurfAI #LiveKit #VoiceAI #FraudDetection #Python #SQLite #AIEngineering
