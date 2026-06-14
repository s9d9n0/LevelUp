import asyncio
import yfinance as yf
import pandas as pd


async def fetch_ohlcv(ticker: str, period: str = "6mo") -> pd.DataFrame:
    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(None, lambda: yf.download(ticker, period=period, auto_adjust=True))
    # Aplatir le MultiIndex des colonnes
    df.columns = df.columns.get_level_values(0)
    return df