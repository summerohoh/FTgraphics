
import os
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timezone
from multiprocessing import Pool

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
kospi200=kospi200.loc[0:200,:]

def extract_adj_price(url):
    page = urlopen(url)
    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(page, "html.parser")
    info_row = soup.find("table", {"data-test":"historical-prices"}).find("tbody").find_all("tr")[0]
    adj_price = info_row.find_all("td")[5].find("span").text.replace(",","")
    adj_price = int(adj_price[:-3]) #strip .00 and convert to number
    return (adj_price)

def epoch_converter(date):
    date = date.replace("/","-")
    date = date + " 0:0:0"
    dateobj=datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    timestamp = int(dateobj.timestamp())
    return timestamp

def get_url():
    links = []
    for row in kospi200.itertuples(index=True, name="stock"):
        url_pair=[]
        if changes['Addition Issue Name'].eq(row[2]).any():
            change_num = changes.index[changes['Addition Issue Name'] == row[2]].tolist()
            #init date is when stock was added to the index
            init_date = epoch_converter(changes.at[change_num[0],'Change Date'])
        else:
            #init date is 12-28-2017
            init_date = epoch_converter('2017/12/28')

        last_date=epoch_converter('2018/12/28')

        #find url for first and lastday
        url1= "https://finance.yahoo.com/quote/"+str(row[1])+".KS/history?period1="+str(init_date)+"&period2="+str(init_date)+"&interval=1d&filter=history&frequency=1d"
        url2= "https://finance.yahoo.com/quote/"+str(row[1])+".KS/history?period1="+str(last_date)+"&period2="+str(last_date)+"&interval=1d&filter=history&frequency=1d"
        url_pair.extend((url1,url2))
        links.append(url_pair)
    return links


def parse(url1, url2, url3):
    #find adj_price for first and lastday
    init_price = extract_adj_price(url1)
    final_price = extract_adj_price(url2)

    #calculate increase in share price
    change = round(((final_price - init_price)/init_price)*100,2)
    sector = extract_sector(url3)

    return change,sector


links_list = get_url()
#share_price_changes = []
with Pool(10) as p:
    result = p.starmap(parse,links_list)
    p.close()
    p.join()


print(share_price_changes)

# Create a column for share price change
kospi200['Share Price Change(%)'] = share_price_changes

#kospi200.to_csv('kospi200_price_changes.csv',index=False)
kospi200.to_csv('kospi200_price_changes.csv',index=False)

#sample url to yahoo finance:
#https://finance.yahoo.com/quote/005930.KS/history?period1=1514646000&period2=1546182000&interval=1d&filter=history&frequency=1d
#https://finance.yahoo.com/quote/298040.KS/history?period1=1515337200&period2=1515337200&interval=1d&filter=history&frequency=1d
#sector labelText__6f58d7c0
#industry labelText__6f58d7c0
