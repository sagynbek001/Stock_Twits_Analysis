import pandas as pd
from example import *
import time

getAveragePriceForWeek("AAPL", pd.to_datetime("2019-1-2").date(), 4)

accuracy_table, alpha_table, counts_table = [str(123)], [str(123)], [str(123)]
sentiment = 1
symbs = ["AAPL"]
initDate = pd.to_datetime("2019-1-2").date()
for i in range(50):
  accuracy_table.append(0.0)
  alpha_table.append(0.0)
  counts_table.append(0)

t1 = time.time()
processSingleRow(1, ["AAPL"], pd.to_datetime("2019-1-2"), accuracy_table, alpha_table, counts_table)
t2 = time.time()
print(f"Time taken: {t2-t1} seconds")

t1 = time.time()
process = True
for symb in symbs:
  if '.' in symb:
    continue
  initialPrice = float(41.7)
  if initialPrice == -1 or initialPrice == 0:
    process = False
    break
  # if (symb in prices.topcryptos or symb in prices.topstocks) and initDate > lastFiveYears:
  #   db.insertIntoStockTable(symbs[0], str(message_id), str(user_id), str(sentiment), str(initDate))
  lastNoResponse = []
  for weekNumber in range(1, 51, 1):
    averageForWeek = 41.7
    if averageForWeek == -1:
      lastNoResponse.append(weekNumber)
      if len(lastNoResponse) >= 2:
        if lastNoResponse[-1] - lastNoResponse[-2] == 1:
          break
      continue
    writtenAccuracyPoints = accuracy_table[weekNumber]
    writtenAlphaPoints = alpha_table[weekNumber]
    writtenCount = counts_table[weekNumber]

    currentAlphaPoint = float(sentiment) * (averageForWeek - initialPrice) / initialPrice
    currentAccuracyPoint = 1 if currentAlphaPoint > 0 else -1

    summationForAccuracy = (writtenCount * writtenAccuracyPoints) + currentAccuracyPoint
    summationForAlpha = (writtenCount * writtenAlphaPoints) + currentAlphaPoint

    counts_table[weekNumber] += 1
    accuracy_table[weekNumber] = summationForAccuracy / counts_table[weekNumber]
    alpha_table[weekNumber] = summationForAlpha / counts_table[weekNumber]

t2 = time.time()
print(f"Time taken: {t2-t1} seconds")

def somefunc(K):
  accum = 0
  for i in range(K):
    if i % 5:
      accum = accum + i
  return accum

t1 = time.time()
somefunc(100_000_000)
t2 = time.time()
print(f"Time taken: {t2-t1} seconds")

t1 = time.time()
somefunc_cy3(100_000_000)
t2 = time.time()
print(f"Time taken: {t2-t1} seconds")