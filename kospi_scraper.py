# import csv
# with open("20181228kospi200_list.csv", mode='r') as csv_file:
#     csv_reader= csv.DictReader(csv_file)
#     first =next(iter(csv_reader))
#     print(first)
#
#     product = first["종목코드"] + ".KS"
#     print(product)

import os
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
from datetime import datetime

os.chdir("/Users/summer/Desktop/FTgraphics")
os.listdir('.')

#load the excel file
file = "20181228kospi200_list_eng.xls"
xl = pd.ExcelFile(file)

#load a sheet into a DataFrame named kospi200
kospi200 = xl.parse(xl.sheet_names[0], converters={'Code':str})

# Filter out unimportant columns
kospi200 = kospi200[['Code','Issue Name', 'Market Cap(KRW)', 'Index Market Cap weight(%)']]

#for testing, slice only 5 iterrows
kospi200=kospi200.loc[0:4,:]


def extract_adj_price(stock_code, yahoo_date_code):
    # specify the url
    page_url = "https://finance.yahoo.com/quote/"+str(stock_code)+".KS/history?period1="+str(yahoo_date_code)+"&period2="+str(yahoo_date_code)+"&interval=1d&filter=history&frequency=1d"
    # query the website and return the html to the variable ‘page’
    page = urlopen(page_url)
    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(page, "html.parser")
    info_row = soup.find("table", {"data-test":"historical-prices"}).find("tbody").find_all("tr")[0]
    adj_price = info_row.find_all("td")[5].find("span").text.replace(",","")
    adj_price = int(adj_price[:-3]) #strip .00 and convert to number
    return (adj_price)


share_price_changes = []

for row in kospi200.itertuples(index=True, name="stock"):

    #dictionary to map dates to yahoo_date_code
    dates = {
    '12-28-2017': '1514386800', #last trading day in 2017
    '12-28-2018': '1545922800', #last trading day in 2018
    }

    # find adj_price for first and lastday
    init_price = extract_adj_price(row[1],dates['12-28-2017'])
    final_price = extract_adj_price(row[1],dates['12-28-2018'])

    #calculate increase in share price
    change = round(((final_price - init_price)/init_price)*100,2)
    share_price_changes.append(change)
    #kospi200 = kospi200.assign(change=p.Series(np.random.randn(sLength)).values)


# Create a column for share price change
kospi200['Share Price Change'] = share_price_changes

kospi200.to_csv('kospi200_price_changes.csv',index=False)



#writer = pd.ExcelWriter('example.xlsx', engine='xlsxwriter')

#sample url to yahoo finance:
#https://finance.yahoo.com/quote/005930.KS/history?period1=1514646000&period2=1546182000&interval=1d&filter=history&frequency=1d
