import os
#mport pandas as pd
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
kosdaq150 = kosdaq150.loc[0:3,:]
url = "http://marketdata.krx.co.kr/contents/MKD/04/0402/04020100/MKD04020100T3T2.jsp"

options = Options()
options.add_argument("--headless")
chromedriver = "/Users/summer/Desktop/FTgraphics/chromedriver"
#driver = webdriver.Chrome(chromedriver)

def extract_krx_price(url):
    driver = webdriver.Chrome(chrome_options=options, executable_path=chromedriver)
    driver.implicitly_wait(50)
    driver.get(url)

    price = None

    try:

        inputStock = driver.find_element_by_class_name("func-finder-input ")
        inputStock.clear()
        inputStock.send_keys("A005930")
        inputFromDate= driver.find_element_by_name("fromdate")
        inputFromDate.clear()
        inputFromDate.send_keys("20181228")
        inputToDate = driver.find_element_by_name("todate")
        inputToDate.clear()
        inputToDate.send_keys("20181228")
        inputToDate.send_keys(Keys.TAB)

        element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "btnidc4ca4238a0b923820dcc509a6f75849b")))

        element.click()
        req = driver.page_source
        soup=BeautifulSoup(req, 'html.parser')

        info_row = soup.find("tbody", {"class":"CI-GRID-BODY-TABLE-TBODY"}).find_all("tr")[0]
        adj_price = info_row.find("td", {"data-name":"tdd_clsprc"}).text.replace(",","")
        price = adj_price

    finally:
        driver.quit()

    return (price)


test = extract_krx_price(url)
print(test)
#
#
# driver = webdriver.Chrome(chrome_options=options, executable_path=chromedriver)
# driver.implicitly_wait(50)
# driver.get(url)
#
# try:
#
#     inputStock = driver.find_element_by_class_name("func-finder-input ")
#     inputStock.clear()
#     inputStock.send_keys("A005930")
#     inputFromDate= driver.find_element_by_name("fromdate")
#     inputFromDate.clear()
#     inputFromDate.send_keys("20181228")
#     inputToDate = driver.find_element_by_name("todate")
#     inputToDate.clear()
#     inputToDate.send_keys("20181228")
#     inputToDate.send_keys(Keys.TAB)
#
#
#     element = WebDriverWait(driver, 20).until(
#     EC.element_to_be_clickable((By.ID, "btnidc4ca4238a0b923820dcc509a6f75849b")))
#
#     element.click()
#     req = driver.page_source
#     soup=BeautifulSoup(req, 'html.parser')
#
#     info_row = soup.find("tbody", {"class":"CI-GRID-BODY-TABLE-TBODY"}).find_all("tr")[0]
#     adj_price = info_row.find("td", {"data-name":"tdd_clsprc"}).text.replace(",","")
#     print(adj_price)
#
# finally:
#     driver.quit()
#
# #
#
# driver.find_element_by_id("btnidd9d4f495e875a2e075a1a4a6e1b9770f").send_keys(Keys.RETURN)


# def get_url():
#     links = []
#     for row in kosdaq150.itertuples(index=True, name="stock"):
#         url_pair=[]
#         init_date = epoch_converter('2017/12/28')
#         last_date=epoch_converter('2018/12/28')
#
#         #find url for first and lastday
#         url1= "https://finance.yahoo.com/quote/"+str(row[1])+".KQ/history?period1="+str(init_date)+"&period2="+str(init_date)+"&interval=1d&filter=history&frequency=1d"
#         url2= "https://finance.yahoo.com/quote/"+str(row[1])+".KQ/history?period1="+str(last_date)+"&period2="+str(last_date)+"&interval=1d&filter=history&frequency=1d"
#
#         url_pair.extend((url1,url2))
#         links.append(url_pair)
#     return links

# def parse(url1, url2):
#
#     return change
#
# links_list = get_url()
#
# with Pool(5) as p:
#     share_price_changes = p.starmap(parse,links_list)
#     p.close()
#     p.join()


# print(share_price_changes)
#
# # Create a column for share price change
# kosdaq150['Share Price Change(%)'] = share_price_changes
#
# #kospi200.to_csv('kospi200_price_changes.csv',index=False)
# kosdaq150.to_csv('test1.csv',index=False)
