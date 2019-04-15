import os
#import pandas as pd
#from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
#from datetime import datetime, timezone
from multiprocessing import Pool
from handlers import load_file,extract_adj_price,epoch_converter
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


os.chdir("/Users/summer/Desktop/FTgraphics")
os.listdir('.')


kosdaq150 = load_file("20181228kosdaq150_list.xls")
kosdaq150 = kosdaq150.loc[0:4,:]
#url = "http://marketdata.krx.co.kr/contents/MKD/04/0402/04020100/MKD04020100T3T2.jsp"

options = Options()
options.add_argument("--headless")
chromedriver = "/Users/summer/Desktop/FTgraphics/chromedriver"
#driver = webdriver.Chrome(chromedriver)
#chrome_options=options


'''extracts closing price from naver finance table'''
def naver_closing_price(stock, page, row):
     driver = webdriver.Chrome(chrome_options=options,executable_path=chromedriver)
     driver.implicitly_wait(50)

     #find initial price
     url = 'https://finance.naver.com/item/sise_day.nhn?code='+stock+'&page='+str(page)
     driver.get(url)
     req = driver.page_source
     soup=BeautifulSoup(req, 'html.parser')
     if int(row)<6:
         info_row = soup.find_all("tr")[int(row)+1]
     else:
         info_row = soup.find_all("tr")[int(row)+4]

     price=info_row.find("span",{"class":"tah p11"}).text.replace(",","")
     driver.quit()

     return (int(price))


def parse(stock):
    #find adj_price for first and lastday
    try:
        init_price = naver_closing_price(stock,31,6)
    except:
        print("error for:initial price " + stock)

    try:
        final_price = naver_closing_price(stock,7,2)
    except:
        print("error for:final price " + stock)

    #calculate increase in share price
    change = round(((final_price - init_price)/init_price)*100,2)
    return init_price, final_price, change


def get_stocks_list():
    stock_list = []
    for row in kosdaq150.itertuples(index=True, name="stock"):
        stock_list.append(row[1])
    return stock_list


test_list=get_stocks_list()
#print(test)
#test=naver_closing_price('067290',7,5)
#8560


with Pool(5) as p:
    results = p.map(parse,test_list)
    p.close()
    p.join()


init_price=[]
final_price=[]
share_price_changes=[]

for row in results:
    init_price.append(row[0])
    final_price.append(row[1])
    share_price_changes.append(row[2])


# Add scraped data columns 
kosdaq150['Price on 20171228'] = init_price
kosdaq150['Price on 20181228'] = final_price
kosdaq150['Share Price Change(%)'] = share_price_changes
kosdaq150['Exchange']='kq'

#kospi200.to_csv('kospi200_price_changes.csv',index=False)
kosdaq150.to_csv('test1.csv',index=False)
