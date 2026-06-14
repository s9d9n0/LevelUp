import asyncio
from data.fetcher import fetch_ohlcv
from indicators.technical import add_indicators

async def main():
    df = await fetch_ohlcv("AAPL")
    df = add_indicators(df)
    print(df.columns.tolist())  # on vérifie que les colonnes sont bien là
    print(df[["Close", "RSI_14"]].tail())

asyncio.run(main())