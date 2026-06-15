import duckdb
import pandas as pd
from datetime import datetime

DB_PATH = "screener.duckdb"


def init_db():
    con = duckdb.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id        INTEGER PRIMARY KEY, 
            date      TIMESTAMP,
            rsi_min   INTEGER,
            rsi_max   INTEGER,
            macd_signal BOOLEAN,
            above_ema   BOOLEAN
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS scan_results (
            scan_id  INTEGER,
            ticker   VARCHAR,
            rsi      DOUBLE,
            close    DOUBLE,
            macd     DOUBLE,
            ema20    DOUBLE
        )
    """)
    con.close()


def save_scan(rsi_min: int, rsi_max: int, macd_signal: bool, above_ema: bool, results: list[dict]) -> int:
    con = duckdb.connect(DB_PATH)

    # Récupère le prochain id
    row = con.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM scans").fetchone()
    scan_id = row[0]

    con.execute("""
        INSERT INTO scans VALUES (?, ?, ?, ?, ?, ?)
    """, [scan_id, datetime.now(), rsi_min, rsi_max, macd_signal, above_ema])

    for r in results:
        con.execute("""
            INSERT INTO scan_results VALUES (?, ?, ?, ?, ?, ?)
        """, [scan_id, r["ticker"], r["rsi"], r["close"], r["macd"], r["ema20"]])

    con.close()
    return scan_id


def get_history() -> list[dict]:
    con = duckdb.connect(DB_PATH)

    rows = con.execute("""
        SELECT s.id, s.date, s.rsi_min, s.rsi_max, s.macd_signal, s.above_ema, COUNT(r.ticker) as nb_resultats
        FROM scans s
        LEFT JOIN scan_results r ON s.id = r.scan_id
        GROUP BY s.id, s.date, s.rsi_min, s.rsi_max, s.macd_signal, s.above_ema
        ORDER BY s.date DESC
    """).fetchall()
    con.close()

    return [
        {
            "id": r[0],
            "date": r[1].strftime("%d/%m/%Y %H:%M"),
            "rsi_min": r[2],
            "rsi_max": r[3],
            "macd_signal": r[4],
            "above_ema": r[5],
            "nb_resultats": r[6],
        }
        for r in rows
    ]


def get_scan_results(scan_id: int) -> list[dict]:
    con = duckdb.connect(DB_PATH)
    
    rows = con.execute("""
        SELECT ticker, rsi, close, macd, ema20
        FROM scan_results
        WHERE scan_id = ?
    """, [scan_id]).fetchall()
    con.close()

    return [
        {"ticker": r[0], "rsi": r[1], "close": r[2], "macd": r[3], "ema20": r[4]}
        for r in rows
    ]