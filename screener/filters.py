import asyncio
from data.fetcher import fetch_ohlcv
from indicators.technical import add_indicators
from config import TICKERS


async def scan_ticker(
    ticker: str,
    rsi_min: int,
    rsi_max: int,
    macd_signal: bool,
    above_ema: bool,
) -> dict | None:
    try:
        df = await fetch_ohlcv(ticker)
        df = add_indicators(df)
        last = df.iloc[-1]

        rsi = last.get("RSI_14")
        if rsi is None:
            return None

        if not (rsi_min <= rsi <= rsi_max):
            return None

        if macd_signal:
            macd = last.get("MACD_12_26_9")
            signal = last.get("MACDs_12_26_9")
            if macd is None or signal is None or macd <= signal:
                return None

        if above_ema:
            ema = last.get("EMA_20")
            close = last.get("Close")
            if ema is None or close is None or close <= ema:
                return None

        return {
            "ticker": ticker,
            "rsi": round(float(rsi), 2),
            "close": round(float(last["Close"]), 2),
            "macd": round(float(last.get("MACD_12_26_9", 0)), 2),
            "ema20": round(float(last.get("EMA_20", 0)), 2),
        }

    except Exception:
        return None


async def run_scan(
    rsi_min: int = 0,
    rsi_max: int = 100,
    macd_signal: bool = False,
    above_ema: bool = False,
) -> list[dict]:
    tasks = [
        scan_ticker(ticker, rsi_min, rsi_max, macd_signal, above_ema)
        for ticker in TICKERS
    ]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]