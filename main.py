from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from screener.filters import run_scan
from data.fetcher import fetch_ohlcv
from indicators.technical import add_indicators

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")

@app.post("/scan", response_class=HTMLResponse)
async def scan(
    request: Request,
    rsi_min: int = Form(0),
    rsi_max: int = Form(100),
    macd_signal: bool = Form(False),
    above_ema: bool = Form(False),
):
    results = await run_scan(
        rsi_min=rsi_min,
        rsi_max=rsi_max,
        macd_signal=macd_signal,
        above_ema=above_ema,
    )
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

