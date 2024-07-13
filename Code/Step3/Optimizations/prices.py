import yfinance as yf
import pandas as pd

def make_set_of_topstocks():
    sptickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    sptickers = set(sptickers.Symbol.to_list())
    sptickers.remove('VLTO')
    sptickers.remove('CEG')
    sptickers.remove('KVUE')
    sptickers.remove('GEHC')
    sptickers.remove('BRK.B') 
    sptickers.remove('BF.B')
    sptickers.remove('ALL')
    sptickers.remove('ON')
    return sptickers

def make_set_of_topcryptos():
    return set(['BTC-USD', 'ETH-USD', 'USDT-USD', 'BNB-USD', 'SOL-USD', 'XRP-USD', 'USDC-USD', 'STETH-USD', 
                'ADA-USD', 'AVAX-USD', 'DOGE-USD', 'TRX-USD', 'DOT-USD', 'LINK-USD', 'MATIC-USD', 
                'WBTC-USD', 'ICP-USD', 'DAI-USD', 'SHIB-USD', 'LTC-USD'])

topstocks = make_set_of_topstocks()
topcryptos = make_set_of_topcryptos()

def create_prices():
    hist = yf.Ticker("JNJ").history(period="10y")
    hist = hist[['Close']]
    hist["JNJ"] = hist['Close']
    hist = hist.drop(columns=['Close'])
    hist.reset_index(inplace = True)
    hist['Date'] = hist['Date'].apply(lambda x: pd.to_datetime(x).date())
    stocksDF = hist.copy()
    stocksDF.set_index('Date', inplace=True)
    stocks_set = set(['JNJ'])

    hist = yf.Ticker("BTC-USD").history(period="10y")
    hist = hist[['Close']]
    hist["BTC-USD"] = hist['Close']
    hist = hist.drop(columns=['Close'])
    hist.reset_index(inplace = True)
    hist['Date'] = hist['Date'].apply(lambda x: pd.to_datetime(x).date())
    cryptosDF = hist.copy()
    cryptosDF.set_index('Date', inplace=True)
    cryptos_set = set(['BTC-USD'])

    return stocksDF, stocks_set, cryptosDF, cryptos_set

def update_prices(df, stocksDF, stocks_set, cryptosDF, cryptos_set):
  stocksDF.reset_index(inplace = True)
  cryptosDF.reset_index(inplace = True)
  for rowNumber in range(len(df)):
    if rowNumber % 10 == 0:
      print(str(rowNumber) + '/' + str(len(df)))
    currentRow = df.iloc[rowNumber].tolist()
    symbs = currentRow[3]
    for symb in symbs:
      if '-USD' in symb:
        if symb not in cryptos_set:
          hist = yf.Ticker(symb).history(period="10y")
          if hist.empty:
             continue
          hist = hist[['Close']]
          hist[symb] = hist['Close']
          hist = hist.drop(columns=['Close'])
          hist.reset_index(inplace = True)
          hist['Date'] = hist['Date'].apply(lambda x: pd.to_datetime(x).date())
          cryptosDF = pd.merge(cryptosDF, hist, on = 'Date', how = 'outer')
          cryptos_set.add(symb)
      else:
        if symb not in stocks_set:
          hist = yf.Ticker(symb).history(period="10y")
          if hist.empty:
             continue
          hist = hist[['Close']]
          hist[symb] = hist['Close']
          hist = hist.drop(columns=['Close'])
          hist.reset_index(inplace = True)
          hist['Date'] = hist['Date'].apply(lambda x: pd.to_datetime(x).date())
          stocksDF = pd.merge(stocksDF, hist, on = 'Date', how = 'outer')
          stocks_set.add(symb)

  stocksDF.set_index('Date', inplace = True)
  stocksDF = stocksDF.sort_index()
  stocksDF.to_csv('../stocks.csv', index = True)

  cryptosDF.set_index('Date', inplace = True)
  cryptosDF = cryptosDF.sort_index()
  cryptosDF.to_csv('../cryptos.csv', index = True)

  return stocksDF, stocks_set, cryptosDF, cryptos_set