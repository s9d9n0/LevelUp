import pandas as pd
import pandas_ta as ta


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df.ta.rsi(append=True)            # RSI_14
    df.ta.macd(append=True)           # MACD_12_26_9
    df.ta.ema(length=20, append=True) # EMA_20
    df.ta.bbands(append=True)         # Bollinger Bands
    return df