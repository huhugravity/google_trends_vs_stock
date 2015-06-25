# Goolge Trends V.S. Stock Fluctuation

This repo is used to play around with Google Trends data. 

Google Trends supports topic search, which means it can distingush different meanings of words. For example, if you type apple, it can provide the option of topic apple company, the results of which will concentrate on the Apple Inc. (and exclude apple fruit).
http://insidesearch.blogspot.com/2013/12/an-easier-way-to-explore-topics-and.html

I use this repo to explore the relationship between seach interest and stock market fluctuation of a certain company. Some plots are saved in the data folder.

Google Trends API comes from https://github.com/dreyco676/pytrends and was modified to comply with Python 2.7.

Stock data is retrieved from yahoo finance historic data, using API https://pypi.python.org/pypi/yahoo-finance/1.2.1. 
