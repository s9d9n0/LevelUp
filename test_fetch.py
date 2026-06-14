import asyncio
from data.fetcher import fetch_ohlcv

async def main():
    df = await fetch_ohlcv("AAPL")
    print(df.tail())

asyncio.run(main())