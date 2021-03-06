# Author: Mike Ferguson
# Version 1.0
#
#
# Python Robinhood Short Term Trading API
import math

import robin_stocks
import pprint
import pandas as pd
import schedule
import time


from datetime import date, timedelta
import calendar

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)


total_profits = []


# -----------------------------------------------------------------------------------------------------------------------
# Function Definitions
def check_stock_prices(df):
    print("Checking Stock Prices...")
    profits = []
    for index, row in df.iterrows():
        symbol = row['Stock']
        shares = row["Quantity"]
        bought_price = float(row["Price"])
        updated_price = float(robin_stocks.stocks.get_latest_price(symbol, includeExtendedHours=True)[0])
        print("Stock: ", symbol, "-----", updated_price, "-----", compare_prices(bought_price, updated_price))
        profit, stock_was_sold = make_decision(updated_price, bought_price, symbol, shares)
        if stock_was_sold:
            total_profits.append(profit)
            row_to_delete = df[df['Stock'] == symbol].index
            dataframe = df.drop(row_to_delete)
            global stocks_left_bool
            if dataframe.empty:
                stocks_left_bool = False
        print("--------------------------------------------")
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print("Time", current_time)
    print("##############################################################################################")
    return


def compare_prices(bought_price, current_price):
    difference = round(current_price - bought_price, 3)
    if difference < 0:
        return "DOWN", difference
    elif difference == 0:
        return "EQUAL", difference
    else:
        return "UP", difference

def get_stock_info(stock):
    results = robin_stocks.account.build_holdings(False)
    status_all = pd.DataFrame.from_dict(results)

    stock_info = status_all
    try:
        stock_info = status_all[stock]
    except KeyError as e:
        print("You have not bought", stock, "yet. Please Quit and Try again.")
        return float('nan'), float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),float('nan')

    current_price = float(stock_info.iloc[0])
    shares = float(stock_info.iloc[1])
    buy_price = float(stock_info.iloc[2])
    total_investment = round(shares * buy_price, 2)
    new_total = round(shares * current_price, 2)
    profit = round(new_total - total_investment, 2)
    percent_profit = round((profit / total_investment) * 100, 2)
    return current_price, buy_price, shares, profit, percent_profit, total_investment, new_total


def make_decision(current_price, bought_price, stock, shares, ):
    percent_gain = (current_price - bought_price) / bought_price * 100
    print("Percent Gain", percent_gain)
    if percent_gain >= 4:
        print("Selling: ", stock)
        # robin_stocks.order_sell_market(stock, shares) # CODE TO ACTUALLY SELL, UNCOMMENT OUT
        new_total = shares * current_price
        old_total = shares * bought_price
        print("Sold", shares, "shares for ", current_price, "each, totaling ", new_total)
        net_profit = new_total - old_total
        return net_profit, True
    else:
        return 0, False


def refresh(df):
    schedule.every(.1666667).minutes.do(check_stock_prices, df)

def check_status(txt_file):

    df_old = pd.read_pickle(txt_file)

    current_prices = []
    buy_prices = []
    profits = []
    percent_profits = []
    total_investments = []
    new_totals = []
    movement = []
    # magnitudes = []

    for index, row in df_old.iterrows():
        symbol = row['Stock']
        current_price, buy_price, shares, profit, percent_profit, total_investment, new_total = get_stock_info(symbol)

        #magnitude = round((current_price - buy_price)  * 100)
        #magnitudes.append(magnitude)
        up_down = compare_prices(buy_price, current_price)[0]
        movement.append(up_down)
        current_prices.append(current_price)
        buy_prices.append(buy_price)
        profits.append(profit)
        percent_profits.append(percent_profit)
        total_investments.append(total_investment)
        new_totals.append(new_total)

    df_old['Current Price'] = current_prices
    df_old["Buy Price"] = buy_prices
    df_old["Profit"] = profits
    df_old["% Profit"] = percent_profits
    df_old['Total Investment'] = total_investments
    df_old["New Total"] = new_totals
    df_old['Up/Down'] = movement


    total_profit = round(df_old['Profit'].sum(), 2)
    total_investment_sum = round(df_old['Total Investment'].sum(), 2)
    if int(total_profit) == 0:
        return
    else:
        roi = round(total_profit / total_investment_sum, 4) * 100
        sum_new = round(total_profit + total_investment_sum, 2)
        print(df_old)
        print()
        print("Total Investment: ", total_investment_sum)
        print("Total Profit: ", total_profit)
        print("ROI: " + str(roi) + "%")
        print("If sold now, you would have $" + str(sum_new))

    # t = time.localtime()
    # current_time = time.strftime("%H:%M:%S", t)
    # print("Time", current_time)

    print("\n--------------------------------------------------------")

def buy():
    # import stocks buying and amount here. Parses Text file to automatically buy stock and quantity

    what_day = input("What File do you want to read/save from? (1) or (2)")
    if what_day.lower() == "1":
        stock_file = open("stocks_to_buy.txt", "r")
    elif what_day.lower() == "2":
        stock_file = open("stocks_to_buy_2.txt", "r")

    stock_names = []
    stock_quantities = []
    stock_list = []
    for stock in stock_file:
        stock_list.append(stock.split())
        stock_names.append(stock.split()[0])
        stock_quantities.append(float(stock.split()[1]))
    df = pd.DataFrame(stock_names, columns=['Stock'])

    # df_old = pd.read_pickle("stocks_to_buy.txt")
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    name_list = []
    price_list = []
    pred_profits = []
    days = []
    days2 = []
    for stock in stock_list:
        symbol = stock[0]
        quantity = stock[1]
        full_name = robin_stocks.stocks.get_name_by_symbol(symbol)
        name_list.append(full_name)
        order_price = float(robin_stocks.stocks.get_latest_price(symbol, includeExtendedHours=True)[0])
        price_list.append(order_price)
        # pred_profit = df_old.loc[df_old.Stock == symbol,'Predicted Profit'].tolist()[0]
        # print("pred Profit", pred_profit)
        #pred_profits.append(pred_profit)
        today = date.today()
        two_days = date.today() + timedelta(2)
        today_name = calendar.day_name[today.weekday()]
        two_days_name = calendar.day_name[two_days.weekday()]
        if today_name == "Thursday":
            days.append(today_name)
            days2.append("Monday")
        elif today_name == "Friday":
            days.append(today_name)
            days2.append("Tuesday")
        else:
            days.append(today_name)
            days2.append(two_days_name)

    df['Full Name'] = name_list
    df['Order Price'] = price_list
    df['Quantity'] = stock_quantities

    print("Entered Buy Mode.")
    print("Reading in Order from txt file...")
    print("Order Input:")
    df['Total Order Amount'] = round(df['Order Price'] * df['Quantity'], 3)
    total_investment = round(df['Total Order Amount'].sum(), 2)
    expected_roi = round(.05 * total_investment, 2)
    total_expected_end = round(total_investment + expected_roi, 2)
    df["% Order Makeup"] = round(((df["Total Order Amount"] / total_investment) * 100), 4)

    df["Order Placed (Evening)"] = days
    df["Day To Sell (Morning)"] = days2
    #df["Predicted Profit/Share"] = pred_profits
    #df["Predicted Profit Total"] = round(pred_profits * df['Quantity'], 3)
    #total_pred_profit = round(df["Predicted Profit Total"].sum(), 2)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print("--------------------------------------------------------\n", df)
    print()
    print("Total Investment: ", total_investment)
    print("Expected ROI (5%): ", expected_roi)
    print("Total Expected End: ", total_expected_end)
    #print("Total Predicted Profit: ", total_pred_profit)
    print("--------------------------------------------------------")
    stocks_left = df.shape[0]

    # ----------------------------------------------------------------------------------------------------------------------

    # confirm and place order
    is_correct = input("\nConfirm Order? y/n")
    if total_investment > buying_power:
        print("Unable to complete, you do not have enough buying power.")
        print("Buying Power: ", buying_power)
        print("Order Total: ", total_investment)
        difference = round(total_investment - buying_power, 2)
        print("Funds Needed: ", difference)
    else:
        if is_correct.lower() == "y":
            print("Placing Order...")
            for index, row in df.iterrows():
                time.sleep(2)
                # robin_stocks.order_buy_market(row["Stock"], row['Quantity']) # UNCOMMENT TO ACTUALLY BUY!!!
                print("Bought", row['Quantity'], "shares of", row['Stock'], "for a total of",
                      row['Total Order Amount'])
            print("Success! Order Placed. Confirmation Email from Robinhood to follow.")

            if what_day.lower() == "1":
                df.to_pickle("stocks_bought.txt")  # where to save it, usually as a .pkl
            elif what_day.lower() == "2":
                df.to_pickle("stocks_bought2.txt")  # where to save it, usually as a .pkl

        else:
            print('Unable to Confirm; Order Aborted.')
    print("--------------------------------------------------------")

def sell():
    what_day = input("What File do you want to read/save from? (1) or (2)")
    if what_day.lower() == "1":
        df_old = pd.read_pickle("stocks_bought.txt")
        confirm = input("Are you sure you want to sell all stock in  ** OLD ** txt file? (y)/(n)")
    elif what_day.lower() == "2":
        confirm = input("Are you sure you want to sell all stock in  ** NEW ** txt file? (y)/(n)")
        df_old = pd.read_pickle("stocks_bought2.txt")
    else:
        print("Mode Not Recognized")
        return

    if confirm.lower() == "y":
        print("Entered Sell Mode.")
        print("Liquidating all stocks in file...")
        df_old['Total Order Amount'] = round(df_old['Price'] * df_old['Quantity'], 2)
        total_investment = round(df_old['Total Order Amount'].sum(), 3)
        expected_roi = round(.05 * total_investment, 2)
        total_expected_end = round(total_investment + expected_roi, 2)
        new_prices = []
        movement = []
        magnitude = []
        mag_percent = []
        dollars_changed = []
        new_worth = []
        for index, row in df_old.iterrows():
            time.sleep(2)
            # robin_stocks.order_sell_market(row["Stock"], row['Quantity']) # UNCOMMENT TO ACTUALLY SELL!!!
            symbol = row['Stock']
            shares = float(row["Quantity"])
            bought_price = float(row["Price"])
            updated_price = float(robin_stocks.stocks.get_latest_price(symbol, includeExtendedHours=True)[0])
            new_prices.append(updated_price)
            result_dir = compare_prices(bought_price, updated_price)[0]
            movement.append(result_dir)
            result = compare_prices(bought_price, updated_price)[1]
            magnitude.append(result)
            percent = (result / bought_price) * 100
            mag_percent.append(percent)
            dollars = round(result * shares, 2)
            dollars_changed.append(dollars)
            new_total_worth = round(shares * updated_price, 2)
            new_worth.append(new_worth)
            print("Sold", row['Quantity'], "shares of", row['Stock'], "at", updated_price, "for a total of",
                  new_total_worth)

        df_old['New Price'] = new_prices
        df_old['Movement'] = movement
        df_old['How Much'] = magnitude
        df_old["How Much %"] = mag_percent
        df_old["Dollars Losed/Gained"] = dollars_changed
        df_old['New Total Worth'] = round(df_old['New Price'] * df_old['Quantity'], 2)
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print("Time", current_time)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print("--------------------------------------------------------\n", df_old)
        print()
        # print("Total Original Investment: ", total_investment)
        # print("Expected ROI (5%): ", expected_roi)
        # print("Total Expected End: ", total_expected_end)
        sum_new = round(df_old['New Total Worth'].sum(), 3)
        print("Sold. You now have", sum_new)
        instant_profit = df_old['Dollars Losed/Gained'].sum()
        instant_ROI = round(instant_profit / total_investment, 4) * 100
        print("Profit: ", instant_profit, "For an ROI of", round(instant_ROI, 4), "percent")
        print("--------------------------------------------------------")
        print("Success! All Stocks Sold. Confirmation Email from Robinhood to follow.")
        print("--------------------------------------------------------")
    else:
        print("Sell Aborted")


# ----------------------------------------------------------------------------------------------------------------------
# Load and print stock Info

# Login and load profile
robin_stocks.authentication.login(username="mef8dd@virginia.edu", password="TargetFingerSunset19!", expiresIn=86400)
print("--------------------------------------------------------")
print("Successfully Logged In")
buying_power = round(float(robin_stocks.profiles.load_account_profile()["portfolio_cash"]), 2)
print("BUYING POWER: ", buying_power)

to_end = False
while to_end is False:
    mode = input("What Mode would you like to enter? Buy(b), Status(s), Run(r), Sell All (sell), or (q) for quit.")
    if mode == "q":
        to_end = True
    print("--------------------------------------------------------")

    if mode.lower() == "b":
        print("Entered Buy Mode.")
        buy()

    # Status Mode: Pulls Current Stock Prices and Info:
    elif mode.lower() == "s":
        print("Entered Status Mode.")
        # my_date = date.today()
        # day = calendar.day_name[my_date.weekday()]
        # two_days = date.today() + timedelta(2)
        # two_days_name = calendar.day_name[two_days.weekday()]
        #
        # if day == "Saturday" or day == "Sunday":
        #     yesterday_name = "Friday"
        #     tomorrow_name = "Tuesday"
        #     two_days_name = "Wednesday"

        what_day = input("What File do you want to check the status of? (1) or (2)")
        if what_day.lower() == "1":
            check_status("stocks_bought.txt")
        elif what_day.lower() == "2":
            check_status("stocks_bought2.txt")

        #check_status("stocks_bought2.txt")


    # Run mode. Starts when the market opens and ends when it closes. Refreshed every 5 seconds
    elif mode == "r":
        # When market opens, check status of stock. If any stock are at 5% or higher, sell. Can change this param.
        # If not, check again in 5 mins.
        print("Entered Run Mode.")
        stocks_left_bool = True
        schedule.every().day.at("09:00:00").do(refresh, df)
        start_time = time.time()
        while True:
            current_time = time.time()
            time_elapsed = start_time - current_time
            # makes sure the trader is between 9am and 6pm
            if time_elapsed < 32460 and stocks_left_bool:
                schedule.run_pending()
            else:
                break

    # Sell Mode: Sells off all Stocks previously bought and gives info.
    elif mode.lower() == "sell":
       sell()

    # Quit Mode: Quits the Program
    elif mode == "q":
        print("Process Quit.")
        to_end = True

    # mode was not recongized
    else:
        print("Unrecognized Input, please try again.")
