
import os
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timezone
from multiprocessing import Process

os.chdir("/Users/summer/Desktop/FTgraphics")
os.listdir('.')

#load the excel file
file = "20181228kospi200_list_eng.xls"
xl = pd.ExcelFile(file)

#load a sheet into a DataFrame named kospi200
kospi200 = xl.parse(xl.sheet_names[0], converters={'Code':str})
# Filter out unimportant columns
kospi200 = kospi200[['Code','Issue Name', 'Market Cap(KRW)', 'Index Market Cap weight(%)']]

#load list of changes in composition for error handling
file_changes = "changes_eng.xls"
xl2 = pd.ExcelFile(file_changes)
changes = xl2.parse(xl2.sheet_names[0])
changes=changes[['Change Date','Addition Issue Name']].dropna()

#manipulate changes file because it's wrong!
#SKCHEM was added on 20180110 for some reason did not work so tried 01/11
changes.at[8, 'Change Date']='2018/01/11'

#for testing, slice only 5 iterrows
#[0,10]returns 11 results so to get 200 need to do 199?
kospi200=kospi200.loc[0:9,:]
#kospi200=kospi200.loc[0:200,:]
#kospi200=kospi200.tail(3)



def extract_adj_price(stock_code, yahoo_date_code):
    # specify the url
    page_url = "https://finance.yahoo.com/quote/"+str(stock_code)+".KS/history?period1="+str(yahoo_date_code)+"&period2="+str(yahoo_date_code)+"&interval=1d&filter=history&frequency=1d"
    # query the website and return the html to the variable ‘page’
    page = urlopen(page_url)
    print(page_url)
    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(page, "html.parser")
    info_row = soup.find("table", {"data-test":"historical-prices"}).find("tbody").find_all("tr")[0]
    adj_price = info_row.find_all("td")[5].find("span").text.replace(",","")
    adj_price = int(adj_price[:-3]) #strip .00 and convert to number
    return (adj_price)


share_price_changes = []

def epoch_converter(date):
    date = date.replace("/","-")
    date = date + " 0:0:0"
    dateobj=datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    timestamp = int(dateobj.timestamp())
    return timestamp

for row in kospi200.itertuples(index=True, name="stock"):

    if changes['Addition Issue Name'].eq(row[2]).any():
        print ("Yo problem here: " + row[2])
        change_num = changes.index[changes['Addition Issue Name'] == row[2]].tolist()
        #init date is when stock was added to the index
        print(change_num)
        init_date = epoch_converter(changes.at[change_num[0],'Change Date'])
        print(init_date)
    else:
        #init diate is 12-28-2017
        init_date = epoch_converter('2017/12/28')



    # find adj_price for first and lastday
    init_price = extract_adj_price(row[1],init_date)
    #print("init_price: " + init_price)
    final_price = extract_adj_price(row[1],epoch_converter('2018/12/28'))
    #print("final_price: " + final_price)

    #calculate increase in share price
    change = round(((final_price - init_price)/init_price)*100,2)
    print (str(row) + row[2])
    share_price_changes.append(change)

# Create a column for share price change
kospi200['Share Price Change(%)'] = share_price_changes

#kospi200.to_csv('kospi200_price_changes.csv',index=False)
kospi200.to_csv('test1.csv',index=False)

#sample url to yahoo finance:
#https://finance.yahoo.com/quote/005930.KS/history?period1=1514646000&period2=1546182000&interval=1d&filter=history&frequency=1d
#https://finance.yahoo.com/quote/298040.KS/history?period1=1515337200&period2=1515337200&interval=1d&filter=history&frequency=1d
#sector labelText__6f58d7c0
#industry labelText__6f58d7c0
