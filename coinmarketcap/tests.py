# import time
# from selenium import webdriver
#
# options = webdriver.ChromeOptions()
# prefs = {"profile.managed_default_content_settings.images": 2}
# options.add_experimental_option("prefs", prefs)
# options.add_argument('--disable-extensions')
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
# while True:
#     try:
#         driver = webdriver.Chrome(chrome_options=options)
#         break
#     except:
#         time.sleep(1)
#
# driver.get('https://mercatox.com/exchange/LEDU/ETH')


import requests
from lxml.html import fromstring

response = requests.get('https://coinmarketcap.com/currencies/education-ecosystem/')
t = fromstring(response.text)

markets = t.xpath('//table[@id="markets-table"]/tbody/tr')
for market in markets:
    name = market.xpath('./td[2]/a/text()')[0]
    pair = market.xpath('./td[3]/a/text()')[0]
    url = market.xpath('./td[3]/a/@href')[0]

    data_usd = market.xpath('./td[4]/span/@data-usd')[0]
    data_btc = market.xpath('./td[4]/span/@data-btc')[0]
    data_native = market.xpath('./td[4]/span/@data-native')[0]

    price_data_usd = market.xpath('./td[5]/span/@data-usd')[0]
    price_data_btc = market.xpath('./td[5]/span/@data-btc')[0]
    price_data_native = market.xpath('./td[5]/span/@data-native')[0]

    volume_percent = market.xpath('./td[6]/span/@data-format-value')[0]
