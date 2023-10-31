import numpy as np
import pandas as pd
import os
import glob
import yfinance as yf
import re
import ast

### Reading files
## read raw csv file
def read_raw(end_file, start_file = 1):
    df_lis = []
    path = "e:\csv_raw\pack_csv_"
    for i in range(start_file, end_file+1):
        sub = pd.read_csv(path+str(i)+'.csv')
        df_lis.append(sub)
    raw = pd.concat(df_lis)
    return raw

## read cleaned CSV file
def read_clean(end_file, start_file = 1):
    path = "e:\csv_clean_1\clean_csv_"
    dflis = []
    for i in range(start_file,end_file+1):
        sub = pd.read_csv(path + str(i) + '.csv')
        dflis.append(sub)
    df = pd.concat(dflis)
    return df


### cleaning data
def claen_raw(df):
    new_df = pd.DataFrame()
    new_df['message_id'] = df['id']

    new_df['body'] = df['body']

    new_df['created_at'] = pd.to_datetime(df['created_at'])

    new_df['user_id'] = [eval(i)['id'] for i in df['user']]
    new_df['symbol'] = [list(j['symbol'] for j in eval(i)) if pd.notna(i) else "NaN" for i in df['symbols']]
    new_df['symbol_mic'] = [list(j['symbol_mic'] for j in eval(i)) if pd.notna(i) else "NaN" for i in df['symbols']]
    new_df['watch_count'] = [list(j['watchlist_count'] for j in eval(i)) if pd.notna(i) else "NaN" for i in df['symbols']]

    new_df['sentiment'] = [eval(i)['sentiment']['basic'] if eval(i)['sentiment'] != None else np.NaN for i in df['entities']]

    new_df['like_count'] = [eval(i)['total'] if pd.notna(i) else "NaN" for i in df['likes']]
    new_df['like_list'] = [eval(i)['user_ids'] if pd.notna(i) else "NaN" for i in df['likes']]

    new_df['parent_message_id'] = [eval(i)['parent_message_id'] if pd.notna(i) else np.NaN for i in df['conversation']]
    new_df.dropna(subset = ['sentiment'], inplace = True)

    return new_df

## aligning data type
def align_type(df):
    df['symbol'] = [eval(i) if pd.notna(i) else np.NaN for i in df['symbol']]
    df['symbol_mic'] = [eval(i) if pd.notna(i) else np.NaN for i in df['symbol_mic']]
    df['watch_count'] = [eval(i) if pd.notna(i) else np.NaN for i in df['watch_count']]
    df['like_list'] = [eval(i) if pd.notna(i) else np.NaN for i in df['like_list']]
    df['parent_message_id'] = df['parent_message_id'].fillna(0).astype(int)

    return df

## plug in symbols for replying message
def plug_in_reply_symbol(df):
    # use1: the reply messages in df
    use1 = df.loc[df['parent_message_id'] != 0]

    # use2: the non-reply messages in df
    use2 = df.loc[df['parent_message_id'] == 0]

    # use3: message-symbol map for merge
    use3 = df[['message_id', 'symbol', 'symbol_mic']].rename(columns = {'message_id':'reply_to_id', 
                                                                        'symbol':'reply_to_symbol',
                                                                        'symbol_mic':'reply_to_mic'})

    # use4: reply messages with the the symbol of its parent message
    use4 = use1.merge(use3, how = 'left', left_on = 'parent_message_id', right_on = 'reply_to_id')

    # use5: assign the symbol of replying message as its parent message's, if there is any
    use5 = use4.copy()
    use5['symbol'] = use5['symbol'].fillna(use5['reply_to_symbol'])
    use5['symbol_mic'] = use5['symbol_mic'].fillna(use5['reply_to_mic'])
    use5.drop(columns = ['reply_to_id','reply_to_symbol', 'reply_to_mic'], inplace = True)

    # use6: concat the symbol_filled reply messages and non-reply messages
    use6 = pd.concat([use5,use2])

    return use6


### Functions for get the prediction result

def check_coin(symlis): 
    # Crypto is denoted differently in stock twits and yfinance, this function aligns the notation
    for i in range(len(symlis)):
        if '.X' in symlis[i]:
            sub = symlis[i].replace('.X','-USD')
            symlis[i] = sub
    return

def get_nth_popular_symbol(df, n):
  c_lis = list(df['symbol'].value_counts().index)

  return c_lis[:n]

def get_interval(df, sym_lis, pre_margin = 10, post_margin = 40):
  df['date'] = pd.to_datetime(df['created_at'])
  result_lis = []
  for i in sym_lis:
    sub = {'symbol':i}
    d_lis = sorted(list(df.loc[df['symbol'] == i]['date']))
    s_d, e_d = d_lis[0], d_lis[-1]
    sub['first_mentioned'] = s_d
    sub['last_mentioned'] = e_d
    result_lis.append(pd.DataFrame([sub]))

  r_df = pd.concat(result_lis)
  r_df['start_check_date'] = r_df['first_mentioned'] - pd.DateOffset(days=pre_margin)
  r_df['end_check_date'] = r_df['last_mentioned'] + pd.DateOffset(days=post_margin)

  return r_df

def get_stock(sym_df):
  result_lis = []
  for symbol, dates in sym_df.set_index('symbol').iterrows():
      if '.X' in symbol:
         symbol = symbol.replace('.X','-USD')
      sub = yf.download(symbol, dates['start_check_date'], dates['end_check_date'])
      sub['ticker'] = symbol
      result_lis.append(sub)
  re = pd.concat(result_lis).reset_index()
  re['Date'] = pd.to_datetime(re["Date"])
  return re

def get_predict_df(df_in,stock_df, pre_lis = [1,3,7,14,28]):
  ticker_set = {i for i in stock_df['ticker']}
  df = df_in.loc[df_in['symbol'].isin(ticker_set)]
  df['date'] =  pd.to_datetime(pd.to_datetime(df['created_at']).dt.date)
  d_lis = ['date']
  for i in pre_lis:
    col = 'date+' + str(i)
    d_lis.append(col)
    df[col] = (df['date'] + pd.DateOffset(days=i))
  use = df

  # use here is the df with date, date + 1, date + 3...
  # merge the stock price & volumn to the dates, 
  #if not exactly equal, merge the closest price date AFTER the check date
  right = stock_df.sort_values(by = 'Date')[['Date', 'ticker', "Close"]]
  right['Date'] = pd.to_datetime(right['Date'])
  for col in d_lis:
    use2= use.sort_values(by = col)
    how = 'backward' if col == 'date' else 'forward'
    use3 = pd.merge_asof(use2, right,
                      left_on = col, right_on = 'Date',
                      left_by = "symbol", right_by = 'ticker',
                      direction=how,suffixes=('', '_'+col))
    use = use3#.drop(columns =["ticker_"+col] )
  re = use[use.columns.drop(list(use.filter(regex = 'ticker')))]
  re2 = re[re.columns.drop(list(re.filter(regex = 'Date')))]
  # print(d_lis)
  return re2.drop(columns = d_lis)


### Functions for computing FA
def check_pre(df):
  df['num_sentiment'] = [1 if i == "Bullish" else -1 for i in df['sentiment']]
  use = df.copy().rename(columns = {'Close':'curr_price'})
  col = [i for i in use.columns if "Close" in i]
  for c in col:
    c_name = '+' + c.split('+')[1]
    use[c_name] = np.sign(use[c] - use['curr_price']) * use['num_sentiment']
    use[c_name] = use[c_name].replace(0.0, 0.5)
    use[c_name] = use[c_name].replace(-1.0, 0.0)
    #use['check'+c_name] = use['num_sentiment'] * use[c_name]
  use2 = use[use.columns.drop(list(use.filter(regex = 'Close')) + ['curr_price', 'num_sentiment'])]
  return use2


def compute_fa(df, by_col = ['user_id'], message_count = True):
  col = [i for i in df.columns if "+" in i]
  use = df[by_col + col]
  re = []
  for c in col:
    sub = use.groupby(by_col)[c].mean()
    re.append(sub)
  re_df = pd.concat(re,axis = 1).reset_index()
  ## get message count
  if message_count:
    col2 = by_col + ['message_id']
    mes_count = df[col2].groupby(by = by_col)['message_id'].count().reset_index().rename(columns = {'message_id':'message_count'})
    return re_df.merge(mes_count, on = by_col).sort_values(by = 'message_count', ascending = False).reset_index().drop(columns = 'index')
  return re_df.reset_index().drop(columns = 'index').dropna()


