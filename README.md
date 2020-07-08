# robinhood
Python CLI API for Short Term Trading in Robinhood

This program is an easy to use Python API for robhinhood short term trading.It is lightweight and incredibly easy to 
use and get started with, as well as easy on your CPU.

Currently, it has three modes:
1) Buy Mode: Using the uploaded stock.txt file, user writes stock ticker and shares desired, 
   and program buys all stock if the account has the funds. Saves the list of bought stocks
   to stocks_bought.txt for the ability to check status later. 

2) Status Mode: Reads in stocks_bought.txt and displays all current information regarding profits and ROI.  

3) Sell Mode: Sells all stock contained in stocks_bought.txt if still in account. Gives info on ROI as well.

4) Run Mode: Automatically opens the trader and looks at all availible stocks. If any stock at opening is at 
   or above a certain percentage(currently 5%), then automatically sell. If not, refreshes at a vaiable time 
   (currently 5 seconds) until 6pm when late market closes. 
