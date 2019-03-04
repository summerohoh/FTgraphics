import pandas as pd
from datetime import datetime, timezone
from urllib.request import urlopen
from bs4 import BeautifulSoup

def load_file(file):
    #load the excel file
    xl=pd.ExcelFile(file)
    #load a sheet into a DataFrame
    data = xl.parse(xl.sheet_names[0], converters={'Code':str})
    # Filter out unimportant columns
    data=data[['Code','Issue Name', 'Market Cap(KRW)', 'Index Market Cap weight(%)']]
    return data

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
