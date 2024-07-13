import pandas as pd

def dateForWeek(initial_date, weekNumber):
  return (initial_date + pd.DateOffset(days = (weekNumber + 1) * 7)).date()