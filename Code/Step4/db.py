import psycopg2
import prices

import pandas as pd
import psycopg2.extras as extras 
import yfinance as yf

from configparser import ConfigParser

def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db

def dropStockTable(stock):
  try:
    params = config()

    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    create_stock_table_query = "DROP TABLE " + str(stock) + ";"

    cursor.execute(create_stock_table_query)
    connection.commit()

  except (Exception, psycopg2.Error) as error:
    print("Failed to create a stock table: ", error)

  finally:
    if connection:
      cursor.close()
      connection.close()

def createStockTables():
  try:
    table_names = []

    for ticker in prices.topstocks:
      ticker = ticker.lower()
      ticker = ticker.replace('-', '_')
      table_names.append('stock_' + ticker)

    for ticker in prices.topcryptos:
      ticker = str(ticker[:-4])
      ticker = ticker.lower()
      ticker = ticker.replace('-', '_')
      table_names.append('crypt_' + ticker)

    params = config()

    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    for name in table_names:
      create_stock_table_query = "CREATE TABLE " + str(name) + " (messageID BIGINT PRIMARY KEY, userID BIGINT NOT NULL, sentiment INT NOT NULL, date DATE);"
      cursor.execute(create_stock_table_query)
      connection.commit()

  except (Exception, psycopg2.Error) as error:
    print("Failed to create a stock table: ", error)

  finally:
    if connection:
      cursor.close()
      connection.close()

def createStockPriceTables(stocks):
  try:
    table_names = []

    for ticker in stocks:
      ticker = ticker.lower()
      ticker = ticker.replace('-', '_')
      if 'usd' in ticker:
        ticker = str(ticker[:-4])
        table_names.append('price_crypt_' + ticker)
      else:
        table_names.append('price_stock_' + ticker)

    params = config()

    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    for name in table_names:
      create_stock_table_query = "CREATE TABLE " + str(name) + " (date DATE PRIMARY KEY, price FLOAT NOT NULL);"
      cursor.execute(create_stock_table_query)
      connection.commit()

  except (Exception, psycopg2.Error) as error:
    pass
    # print("Failed to create a stock table: ", error)

  finally:
    if connection:
      cursor.close()
      connection.close()

def insertToStockPriceTables(stocks):
  try:
    params = config()

    connection = psycopg2.connect(**params)
    cursor = connection.cursor() 

    progress = 0
    for stock in stocks:
      progress += 1
      if progress % 10 == 0:
        print(str(progress) + '/' + len(stocks))
      hist = yf.Ticker(stock).history(period="10y")
      hist = hist[['Close']]
      hist['price'] = hist['Close']
      hist = hist.drop(columns=['Close'])
      hist.reset_index(inplace = True)
      hist['date'] = hist['Date'].apply(lambda x: pd.to_datetime(x).date())
      hist = hist.drop(columns=['Date'])

      tuples = [tuple(x) for x in hist.to_numpy()] 
  
      cols = ','.join(list(hist.columns))

      ticker = stock.lower()
      ticker = ticker.replace('-', '_')
      if 'usd' in ticker:
        ticker = str(ticker[:-4])
        ticker = 'price_crypt_' + ticker
      else:
        ticker = 'price_stock_' + ticker

      query = "INSERT INTO %s(%s) VALUES %%s" % (ticker, cols) 

      extras.execute_values(cursor, query, tuples) 
      connection.commit()
      
  except (Exception, psycopg2.Error) as error:
    pass
    # print("Failed to create a stock table: ", error)

  finally:
    if connection:
      cursor.close()
      connection.close()

def getPriceForDate(ticker, date):
  try:
    # read connection parameters
    params = config()

    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    ticker = ticker.lower()
    ticker = ticker.replace('-', '_')
    if 'usd' in ticker:
      ticker = str(ticker[:-4])
      ticker = 'price_crypt_' + ticker
    else:
      ticker = 'price_stock_' + ticker
        
    query = """ 
    SELECT * 
    FROM
    """
    query += ticker
    query += """
    WHERE date = %s
    """

    cursor.execute(query, (str(date),))

    connection.commit()
    result = cursor.fetchall()
    return result

  except (Exception, psycopg2.Error) as error:
    print("Failed to select a record from the table: ", error)

  finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()

def insertToStockTable(stock, row):
  try:
    params = config()

    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    create_stock_table_query = """ 
    INSERT INTO counts_table
    (userid, week1, week2, week3, week4, week5, week6, week7, week8, week9, week10, week11, week12, week13, week14, week15, week16, week17, week18, week19, week20, week21, week22, week23, week24, week25, week26, week27, week28, week29, week30, week31, week32, week33, week34, week35, week36, week37, week38, week39, week40, week41, week42, week43, week44, week45, week46, week47, week48, week49, week50) 
    VALUES 
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(create_stock_table_query)
    connection.commit()

  except (Exception, psycopg2.Error) as error:
    print("Failed to create a stock table: ", error)

  finally:
    if connection:
      cursor.close()
      connection.close()

def insertToFilesTable(file_id):
  try:
    params = config()

    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    query = """ 
    INSERT INTO files_processed
    (fileid)
    VALUES 
    (%s)
    """
    cursor.execute(query, (file_id,))
    connection.commit()

  except (Exception, psycopg2.Error) as error:
    print("Failed to insert the file into the table: ", error)

  finally:
    if connection:
      cursor.close()
      connection.close()

def selectAccuracy(userID, table_name):
  try:
    # read connection parameters
    params = config()

    connection = psycopg2.connect(**params)
    cursor = connection.cursor()
        
    postgres_insert_query = """ 
    SELECT * 
    FROM """ + table_name + """
    WHERE userid = %s
    """

    cursor.execute(postgres_insert_query, (userID,))

    connection.commit()
    result = cursor.fetchall()
    return result

  except (Exception, psycopg2.Error) as error:
    print("Failed to select a record from the table: ", error)

  finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()

def deleteAll():
  try:
    # read connection parameters
    params = config()

    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    postgres_delete_query_accuracy_table = """ 
    DELETE FROM accuracy_table
    """

    postgres_delete_query_alpha_table = """ 
    DELETE FROM alpha_table
    """

    postgres_delete_query_counts_table = """ 
    DELETE FROM counts_table
    """

    cursor.execute(postgres_delete_query_accuracy_table)
    connection.commit()
    count = cursor.rowcount

    cursor.execute(postgres_delete_query_alpha_table)
    connection.commit()
    count = cursor.rowcount

    cursor.execute(postgres_delete_query_counts_table)
    connection.commit()
    count = cursor.rowcount

  except (Exception, psycopg2.Error) as error:
    print("Failed to delete all records from the tables: ", error)

  finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()

def remove(userID, table_name):
  try:
    # read connection parameters
    params = config()

    connection = psycopg2.connect(**params)
    cursor = connection.cursor()
        
    query = "DELETE FROM " + table_name + " WHERE userid = %s"

    cursor.execute(query, (userID,))
    connection.commit()

  except (Exception, psycopg2.Error) as error:
    print("Failed to drop a record from the table: ", error)

  finally:
    # closing database connection.
    if connection:
      cursor.close()
      connection.close()

def insert(accuracy_table_row, alpha_table_row, counts_table_row):
  try:
    # read connection parameters
    params = config()

    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    postgres_insert_query_accuracy_table = """ 
    INSERT INTO accuracy_table
    (userid, week1, week2, week3, week4, week5, week6, week7, week8, week9, week10, week11, week12, week13, week14, week15, week16, week17, week18, week19, week20, week21, week22, week23, week24, week25, week26, week27, week28, week29, week30, week31, week32, week33, week34, week35, week36, week37, week38, week39, week40, week41, week42, week43, week44, week45, week46, week47, week48, week49, week50) 
    VALUES 
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    postgres_insert_query_alpha_table = """ 
    INSERT INTO alpha_table
    (userid, week1, week2, week3, week4, week5, week6, week7, week8, week9, week10, week11, week12, week13, week14, week15, week16, week17, week18, week19, week20, week21, week22, week23, week24, week25, week26, week27, week28, week29, week30, week31, week32, week33, week34, week35, week36, week37, week38, week39, week40, week41, week42, week43, week44, week45, week46, week47, week48, week49, week50) 
    VALUES 
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    postgres_insert_query_counts_table = """ 
    INSERT INTO counts_table
    (userid, week1, week2, week3, week4, week5, week6, week7, week8, week9, week10, week11, week12, week13, week14, week15, week16, week17, week18, week19, week20, week21, week22, week23, week24, week25, week26, week27, week28, week29, week30, week31, week32, week33, week34, week35, week36, week37, week38, week39, week40, week41, week42, week43, week44, week45, week46, week47, week48, week49, week50) 
    VALUES 
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    if accuracy_table_row != None:
      remove(accuracy_table_row[0], 'accuracy_table')
      record_to_insert = tuple(accuracy_table_row)
      cursor.execute(postgres_insert_query_accuracy_table, record_to_insert)
    elif alpha_table_row != None:
      remove(alpha_table_row[0], 'alpha_table')
      record_to_insert = tuple(alpha_table_row)
      cursor.execute(postgres_insert_query_alpha_table, record_to_insert)
    else:
      remove(counts_table_row[0], 'counts_table')
      record_to_insert = tuple(counts_table_row)
      cursor.execute(postgres_insert_query_counts_table, record_to_insert)

    connection.commit()
    count = cursor.rowcount

  except (Exception, psycopg2.Error) as error:
    print("Failed to insert record into the table: ", error)

  finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()

def insertIntoStockTable(stock, message_id, user_id, sentiment, initDate):
  try:
    # read connection parameters
    params = config()

    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    ticker = stock.lower()
    ticker = ticker.replace('-', '_')
    if 'usd' in ticker:
      ticker = str(ticker[:-4])
      ticker = 'crypt_' + ticker
    else:
      ticker = 'stock_' + ticker
  
    query = """ 
    INSERT INTO """ + ticker + """ 
    (messageid, userid, sentiment, date)
    VALUES
    (%s,%s,%s,%s)
    """

    record_to_insert = (message_id, user_id, sentiment, str(initDate))
    cursor.execute(query, record_to_insert)

    connection.commit()
    count = cursor.rowcount

  except (Exception, psycopg2.Error) as error:
    # print("Failed to insert record into the table: ", error)
    pass

  finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()