# Introduction
Stock twits is an online platform where people share their ideas on financial market by makings posts. This project focuses on exploratory analysis of the data and tries to figure out what more can be done with it. 

The raw data is grabbed by Nasser Alansari (alansari.n@nyu.edu) from the stock twits website. The data contains around 400 million messages with corresponding information such as posting time, user id, tickers, and sentiment for each of the messages. The general idea of the analysis is to find out if the bullish or bearish perspective on stocks can be continously accurate throughout the time. 

This project is supervised by Professor Aaron Kaufman (aaronkaufman@nyu.edu).

## Some explanation of the notebooks
### data_pack
The data_pack.ipynb notebook is used for repacking data to csv files. In the old version of web grabber, the data is packed in small zipped json files while in the recent version they have been converted to small csv files. In this notebook, we roughly cleaned the data (such as drop useless rows and keep the useful columns) and packed them in a relatively large scale for easy accessing.

### part_data_analysis
This is the main analysis notebook. In this notebook, we roughly divide the whole data set into 4 quarters (by simply concatinating the packed data from data_pack notebook). For each of the quarter, we try to compute the "forecast accuracy" of the users and save it into FA files for further analysis.

#### Logic of forecast accuracy
For a message post, we find the ticker code (stock) it mentions, the sentiment of the user (bullish or bearish), and also the date of the post. Based on the date and ticker code, we grab the true stock price data from yfinance package. With the true price data, we compare the the price for the post date with the price a few days later (+ 1, 3, 7, 11, 14, 28 days). If the price goes align with the sentiment (if the price goes up while the sentiment is bullish and vise versa), we set the "outcome" of the post as +1, if it goes against the sentiment, we set it to -1, if it stays the same, we set 0. For the "forecast accuracy", we group by user and take the average of the "outcomes".

### utils
This py file contains a few functions that would be used in the analysis for easy calling as there are a lot of notebooks doing similar tasks. Along the progress of the project I just uploaded the most conprehensive ones here. 

### FA_analysis
This notebook is the analysis of the FA files. It produces the FA distribution of the FAs of each quarters. And also analyses the FA cross quarters to find the users who are continuously doing good / bad.

## Possible future directions
#### Fill the sentiment with NLP model
In the analysis we lose a lot of messages because some of the users did not label their posts. NLP or other ML models that can recognize the sentiment of the messages with high accuracy could be a direction for growth.

#### Message level analysis
For now we have filtered out the continuously good / bad users, we can check some of them in detail and possibly do social network among the users.
