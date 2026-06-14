from data.fetcher import fetch_ohlcv
from indicators.technical import add_indicators
from config import TICKERS


async def run_scan(
    rsi_max: int = 35,
    rsi_min: int = 0,
    macd_signal: bool = False,
    above_ema: bool = False,
) -> list[dict]:
    results = []

    for ticker in TICKERS:
        df = await fetch_ohlcv(ticker)
        df = add_indicators(df)
        last = df.iloc[-1]

        rsi = last.get("RSI_14")
        if rsi is None:
            continue

        # Filtre RSI
        if not (rsi_min <= rsi <= rsi_max):
            continue

        # Filtre croisement MACD (MACD > Signal = momentum haussier)
        if macd_signal:
            macd = last.get("MACD_12_26_9")
            signal = last.get("MACDs_12_26_9")
            if macd is None or signal is None or macd <= signal:
                continue

        # Filtre prix au-dessus de l'EMA 20
        if above_ema:
            ema = last.get("EMA_20")
            close = last.get("Close")
            if ema is None or close is None or close <= ema:
                continue

        results.append({
            "ticker": ticker,
            "rsi": round(float(rsi), 2),
            "close": round(float(last["Close"]), 2),
            "macd": round(float(last.get("MACD_12_26_9", 0)), 2),
            "ema20": round(float(last.get("EMA_20", 0)), 2),
        })

    return results