import sqlite3
import os
from datetime import datetime
from livekit.agents import function_tool
import asyncio

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "shared-data", "fraud_cases.db")


def _db_read(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    colnames = [c[0] for c in cur.description]
    conn.close()
    return [dict(zip(colnames, row)) for row in rows]


def _db_write(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()


# ----------- ASYNC TOOLS (important!) -----------

@function_tool
async def load_case(user_name: str):
    return await asyncio.to_thread(
        _db_read,
        "SELECT * FROM fraud_cases WHERE LOWER(user_name)=LOWER(?) LIMIT 1",
        (user_name,)
    )


@function_tool
async def verify_answer(user_name: str, answer: str):
    rows = await asyncio.to_thread(
        _db_read,
        "SELECT verification_answer FROM fraud_cases WHERE LOWER(user_name)=LOWER(?)",
        (user_name,)
    )
    if not rows:
        return {"verified": False}

    return {"verified": rows[0]["verification_answer"].lower() == answer.lower()}


@function_tool
async def update_case_status(user_name: str, status: str, note: str):
    await asyncio.to_thread(
        _db_write,
        """
        UPDATE fraud_cases
        SET status=?, notes=?, updated_at=?
        WHERE LOWER(user_name)=LOWER(?)
        """,
        (status, note, datetime.utcnow().isoformat(), user_name)
    )
    return {"updated": True, "status": status, "note": note}
