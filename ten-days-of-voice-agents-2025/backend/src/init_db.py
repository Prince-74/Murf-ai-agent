import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "shared-data", "fraud_cases.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS fraud_cases (
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
)
""")

# Insert 5 fake sample fraud cases
cases = [
    ("John", "12345", "4242", "₹3,999", "ABC Industries",
     "2025-02-10 14:21", "e-commerce", "alibaba.com",
     "What is your favorite color?", "blue", "pending_review"),

    ("Ravi", "99887", "1122", "₹12,450", "Flipkart Electronics",
     "2025-02-05 09:15", "online retail", "flipkart.com",
     "What city were you born in?", "delhi", "pending_review"),

    ("Aisha", "87654", "9900", "₹899", "Spotify Subscription",
     "2025-02-03 22:10", "digital services", "spotify.com",
     "What is your pet's name?", "milo", "pending_review"),

    ("Karan", "55331", "7700", "₹25,000", "Myntra Fashion",
     "2025-02-08 11:45", "shopping", "myntra.com",
     "What is your favorite food?", "pasta", "pending_review"),

    ("Meera", "44119", "6644", "₹2,499", "Zara Clothing",
     "2025-02-01 17:35", "retail", "zara.com",
     "What is your school name?", "dps", "pending_review"),

     ("Alex", "33221", "5566", "₹5,750", "Netflix Subscription",
     "2025-02-09 20:00", "digital services", "netflix.com",
     "What is your favorite movie?", "inception", "pending_review"),

     ("Sana", "22110", "3344", "₹1,299", "Amazon Prime",
     "2025-02-04 13:25", "online retail", "amazon.com",
     "What is your mother's maiden name?", "khan", "pending_review")
     

]

cur.executemany("""
INSERT INTO fraud_cases (
    user_name, security_identifier, card_ending, amount, merchant,
    timestamp, category, source, verification_question, verification_answer, status
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", cases)

conn.commit()
conn.close()

print("SQLite database initialized with 5 sample cases!")
