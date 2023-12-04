# SmartMaple Python Project Homework

Web Scraping, Data Analyzing, Warehousing

## Table of Contents

- [About](#about)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)

## About

It can perform data analysis by simultaneously pulling data from the news site, keeping the data in certain columns, visualizing it with a graph as a result of this analysis, saving the captured data to the MongoDB database, showing data grouped according to the update time from the saved database, keeping data on the scalability and efficiency of the code, and allowing error code tracking. It is a Python program that allows

## Getting Started

### Prerequisites
Requires these libraries:
itertools, matplotlib, pandas, requests, BeautifulSoup, pymongo, datetime, groupby,logging


### Installation
There should be installed MongoDB in computer.

## Usage
frequentWordsFromAllNews(final_matrix) and Graphs(most_frequent_ten_words, number_of_news, number_of_words) functions:
During the data analysis phase, the news from the 50 pages of the website were extracted and entered into each one, and a table was created with the desired data. These data contain ["url", "header", "summary", "text", "img_url_list", "publish_date", "update_date"] information respectively. Among these columns, the text column was taken from each news and each word was counted by creating a pool. This function produces graphics with the png extension. As expected, it was observed that prepositions were at a remarkably high rate in these frequencies.

final_matrix= is the matrix containing [number of news][number of columns] where all data is kept.
most_frequent_ten_words, = the first 10 words in the dictionary and their frequency values are sorted from largest to smallest.
number_of_news = number of news captured
number_of_words = the sum of the words in the text column of all news.
These values are only included in the chart to help us understand it statistically.

Log Informations:
Since this pipeline contains many continuous steps, logging was used to track and prevent errors. Since the data we want to access is kept on the website, it is important that the site is accessible at the beginning. It is considered successful as it means that we can reach the status_code when it is 200. Otherwise, it will write whatever error is received from the site. To update our Stats table, we count the successful and unsuccessful counts we get from here. At the same time, elapsed_time is calculated by calculating the time interval at the beginning and end of the Pagination function, and the date when data capture started is also recorded.
The next logging step follows the step of updating our stats table in MongoDB. The same process is kept when saving the FrequentWord result.
