import pandas as pd

def symbolsToList(symbols: str):
    symbols = symbols[1:-1]
    symbols = symbols.split(',')
    toReturn = []
    for symb in symbols:
        symb = symb.split("'")
        toReturn.append(symb[1])
    return toReturn

def readData(path: str):
  df = pd.read_csv(path)
  df['symbols'] = df['symbols'].apply(symbolsToList)
  df['date'] = df['date'].apply(lambda x: pd.to_datetime(x).date())
  return df