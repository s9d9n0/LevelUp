from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from data.db import init_db, save_scan, get_history, get_scan_results
from data.fetcher import fetch_ohlcv
from screener.filters import run_scan
from indicators.technical import add_indicators

import io
import csv

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup():
    init_db()



@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    history = get_history()
    print("historique:", history)
    return templates.TemplateResponse(request, "dashboard.html", {"history": history})


@app.post("/scan", response_class=HTMLResponse)
async def scan(
    request: Request,
    rsi_min: int = Form(0),
    rsi_max: int = Form(100),
    macd_signal: bool = Form(False),
    above_ema: bool = Form(False)):
    results = await run_scan(
        rsi_min=rsi_min,
        rsi_max=rsi_max,
        macd_signal=macd_signal,
        above_ema=above_ema,
    )
    scan_id = save_scan(rsi_min, rsi_max, macd_signal, above_ema, results)
    print("scan sauvegardé, id:", scan_id, "nb résultats:", len(results))
    return templates.TemplateResponse(request, "partials/results_table.html",
        {"results": results})



@app.get("/export", response_class=StreamingResponse)
async def export(
    request: Request,
    rsi_min: int = 0,
    rsi_max: int = 100,
    macd_signal: bool = False,
    above_ema: bool = False,
):
    results = await run_scan(
        rsi_min=rsi_min,
        rsi_max=rsi_max,
        macd_signal=macd_signal,
        above_ema=above_ema,
    )

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["ticker", "name", "close", "variation", "rsi", "macd", "ema20"])
    writer.writeheader()
    writer.writerows(results)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=screener.csv"}
    )



@app.get("/history/{scan_id}", response_class=HTMLResponse)
async def history_detail(request: Request, scan_id: int):
    results = get_scan_results(scan_id)
    return templates.TemplateResponse(request, "partials/results_table.html", {"results": results})



@app.get("/chart/{ticker}", response_class=HTMLResponse)
async def chart(request: Request, ticker: str):
    df = await fetch_ohlcv(ticker)
    df = add_indicators(df)
    df = df.reset_index()

    candles = []
    rsi_data = []

    for _, row in df.iterrows():
        date = row["Date"].strftime("%Y-%m-%d")
        candles.append({
            "x": date,
            "o": round(float(row["Open"]), 2),
            "h": round(float(row["High"]), 2),
            "l": round(float(row["Low"]), 2),
            "c": round(float(row["Close"]), 2),
        })
        rsi_val = row.get("RSI_14")
        rsi_data.append({
            "x": date,
            "y": round(float(rsi_val), 2) if rsi_val and not str(rsi_val) == "nan" else None
        })

    return templates.TemplateResponse(request, "chart.html", {
        "ticker": ticker,
        "candles": candles,
        "rsi_data": rsi_data,
    })

