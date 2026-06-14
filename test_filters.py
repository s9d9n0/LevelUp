import asyncio
from screener.filters import run_scan

async def main():
    results = await run_scan(rsi_max=60)  # seuil large pour avoir des résultats
    for r in results:
        print(r)

asyncio.run(main())