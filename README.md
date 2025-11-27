🛡️ Day 6 – Fraud Alert Voice Agent (LiveKit + Murf Falcon + SQLite)
Welcome to Day 6 of the Murf AI Voice Agents Challenge!

In this project, I built a Fraud Alert Voice Agent for a fictional bank using LiveKit Agents, Murf Falcon TTS, Deepgram STT, Gemini Flash, and SQLite as the fraud-case database.
This agent behaves exactly like a real bank’s fraud-prevention representative — but using safe, fake data only.
🚨 Project Overview
The Fraud Alert Agent automatically:
Loads a fraud case from an SQLite database
Verifies the caller using a non-sensitive security question
Reads out suspicious transaction details
Asks the user to confirm or deny the transaction
Updates the fraud case as safe or fraudulent
Logs the result back into the database

This entire interaction runs inside LiveKit's real-time voice session, powered by Murf Falcon’s ultra-fast TTS engine.
🎯 Features (MVP)
🔍 1. Fake Fraud Case Database (SQLite)
Each case contains:
Plain text
ANTLR4
Bash
C
C#
CSS
CoffeeScript
CMake
Dart
Django
Docker
EJS
Erlang
Git
Go
GraphQL
Groovy
HTML
Java
JavaScript
JSON
JSX
Kotlin
LaTeX
Less
Lua
Makefile
Markdown
MATLAB
Markup
Objective-C
Perl
PHP
PowerShell
.properties
Protocol Buffers
Python
R
Ruby
Sass (Sass)
Sass (Scss)
Scheme
SQL
Shell
Swift
SVG
TSX
TypeScript
WebAssembly
YAML
XML

{
  "user_name": "John",
  "security_identifier": "12345",
  "card_ending": "4242",
  "amount": "₹3,999",
  "merchant": "ABC Industries",
  "timestamp": "2025-02-10 14:21",
  "category": "e-commerce",
  "source": "alibaba.com",
  "verification_question": "What is your favorite color?",
  "verification_answer": "blue",
  "status": "pending_review"
}



(5 fake sample cases are inserted.)
🗣️ 2. Realistic Fraud Department Persona
The agent:
Introduces itself as SecureBank Fraud Department
Speaks calmly, professionally, and concisely
Never asks for PINs, full card numbers, or any sensitive data
Uses only the information in your database tools

🔐 3. Safe Verification Flow
Ask for the caller’s name
Load fraud case via load_case(name)
Ask the stored verification question
Confirm via verify_answer(name, answer)

If verification fails → end call politely.
🧾 4. Transaction Review Flow
If verified:
Read merchant, amount, time, masked card, category
Ask “Did you make this transaction?”

If Yes → mark case confirmed_safe

If No → mark case confirmed_fraud
All updates are saved using update_case_status(...).
🛠️ Tech Stack
ComponentTechnologyVoice → TextDeepgram Nova-3Text → VoiceMurf Falcon (Matthew)LLMGoogle Gemini 2.5 FlashDatabaseSQLiteRuntimeLiveKit Voice AgentsToolsCustom function_tools
📂 Project Structure
Plain text
ANTLR4
Bash
C
C#
CSS
CoffeeScript
CMake
Dart
Django
Docker
EJS
Erlang
Git
Go
GraphQL
Groovy
HTML
Java
JavaScript
JSON
JSX
Kotlin
LaTeX
Less
Lua
Makefile
Markdown
MATLAB
Markup
Objective-C
Perl
PHP
PowerShell
.properties
Protocol Buffers
Python
R
Ruby
Sass (Sass)
Sass (Scss)
Scheme
SQL
Shell
Swift
SVG
TSX
TypeScript
WebAssembly
YAML
XML

backend/
│
├── src/
│   ├── agent.py              # Main Fraud Agent logic
│   ├── fraud_tools.py        # SQLite functions via function_tool
│   ├── init_db.py            # Creates fraud_cases.db with sample data
│
├── shared-data/
│   └── fraud_cases.db        # SQLite database
│
└── README.md



▶️ How to Run
1. Create SQLite DB
Plain text
ANTLR4
Bash
C
C#
CSS
CoffeeScript
CMake
Dart
Django
Docker
EJS
Erlang
Git
Go
GraphQL
Groovy
HTML
Java
JavaScript
JSON
JSX
Kotlin
LaTeX
Less
Lua
Makefile
Markdown
MATLAB
Markup
Objective-C
Perl
PHP
PowerShell
.properties
Protocol Buffers
Python
R
Ruby
Sass (Sass)
Sass (Scss)
Scheme
SQL
Shell
Swift
SVG
TSX
TypeScript
WebAssembly
YAML
XML

python src/init_db.py



2. Start LiveKit Worker
Plain text
ANTLR4
Bash
C
C#
CSS
CoffeeScript
CMake
Dart
Django
Docker
EJS
Erlang
Git
Go
GraphQL
Groovy
HTML
Java
JavaScript
JSON
JSX
Kotlin
LaTeX
Less
Lua
Makefile
Markdown
MATLAB
Markup
Objective-C
Perl
PHP
PowerShell
.properties
Protocol Buffers
Python
R
Ruby
Sass (Sass)
Sass (Scss)
Scheme
SQL
Shell
Swift
SVG
TSX
TypeScript
WebAssembly
YAML
XML

python src/agent.py



3. Open the Voice Assistant Playground
Connect and test!

Ask:
Plain text
ANTLR4
Bash
C
C#
CSS
CoffeeScript
CMake
Dart
Django
Docker
EJS
Erlang
Git
Go
GraphQL
Groovy
HTML
Java
JavaScript
JSON
JSX
Kotlin
LaTeX
Less
Lua
Makefile
Markdown
MATLAB
Markup
Objective-C
Perl
PHP
PowerShell
.properties
Protocol Buffers
Python
R
Ruby
Sass (Sass)
Sass (Scss)
Scheme
SQL
Shell
Swift
SVG
TSX
TypeScript
WebAssembly
YAML
XML

Hello
My name is John
Blue
No, I didn't make this transaction



You will see:
Case loaded
Verification success
Fraud confirmed
Database updated

📤 Git Commands to Push This Project
Plain text
ANTLR4
Bash
C
C#
CSS
CoffeeScript
CMake
Dart
Django
Docker
EJS
Erlang
Git
Go
GraphQL
Groovy
HTML
Java
JavaScript
JSON
JSX
Kotlin
LaTeX
Less
Lua
Makefile
Markdown
MATLAB
Markup
Objective-C
Perl
PHP
PowerShell
.properties
Protocol Buffers
Python
R
Ruby
Sass (Sass)
Sass (Scss)
Scheme
SQL
Shell
Swift
SVG
TSX
TypeScript
WebAssembly
YAML
XML

git init
git add .
git commit -m "Day 6 – Fraud Alert Voice Agent completed"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main



🌟 LinkedIn Post (Ready to Use)
🚨 Day 6 of the #10DaysofAIVoiceAgents Challenge!

Today I built a Fraud Alert Voice Agent using LiveKit Agents, Murf Falcon TTS, Deepgram STT, Gemini Flash, and SQLite.
This voice agent acts like a real bank fraud rep — but using completely safe, fake data.
💡 What it does:
Loads fraud cases from SQLite
Verifies the user with a safe question (no PINs, no sensitive data!)
Reads suspicious transactions
Asks “Did you make this transaction?”
Marks it Safe or Fraudulent
Updates the database in real time

🎤 The entire flow happens inside a seamless LiveKit voice session with ultra-fast Murf Falcon TTS.
This was one of the most realistic real-world voice-AI workflows I’ve built — and it’s amazing to see everything working end-to-end.
Excited for Day 7! 🚀
#MurfAIVoiceAgentsChallenge #10DaysOfAIVoiceAgents #VoiceAI #LiveKit #MurfAI #SQLite #FraudDetection



