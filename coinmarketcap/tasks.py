import time
import requests
from lxml.html import fromstring
import cfscrape
from etherscan.celery import app
from coinmarketcap.models import *


def exrates_api(pair):
    ticker = requests.get('https://exrates.me/openapi/v1/public/ticker?currency_pair=' + pair).json()
    if not ticker:
        ticker = {
            'last': 0,
            'lowestAsk': 0,
            'highestBid': 0,
        }
    else:
        ticker = ticker[0]
    orderbook = requests.get('https://exrates.me/openapi/v1/public/orderbook/' + pair).json()
    return ticker, orderbook


@app.task
def exrates_data(timestamp, source_pk, market_pk):
    source = Source.objects.get(id=source_pk)
    market = Market.objects.get(id=market_pk)
    if 'LEDU/BTC' == source.pair:
        ticker, orderbook = exrates_api('ledu_btc')
    elif 'LEDU/ETH' == source.pair:
        ticker, orderbook = exrates_api('ledu_eth')
    market.current_price = ticker['last']
    market.lowest_ask = ticker['lowestAsk']
    market.highest_bid = ticker['highestBid']
    market.save()

    buys = orderbook['BUY']
    sells = orderbook['SELL']
    for buy in buys:
        order = OrderBook(timestamp=timestamp, source=source, amount=buy['amount'], rate=buy['rate'], type=True)
        order.save()
    for sell in sells:
        order = OrderBook(timestamp=timestamp, source=source, amount=sell['amount'], rate=sell['rate'], type=False)
        order.save()


def livecoin_api(pair):
    ticker = requests.get('https://api.livecoin.net/exchange/ticker?currencyPair=' + pair).json()
    orderbook = requests.get('https://api.livecoin.net/exchange/order_book?currencyPair=' + pair + '&groupByPrice=true').json()
    return ticker, orderbook


@app.task
def livecoin_data(timestamp, source_pk, market_pk):
    source = Source.objects.get(id=source_pk)
    market = Market.objects.get(id=market_pk)
    if 'LEDU/BTC' == source.pair:
        ticker, orderbook = livecoin_api('LEDU/BTC')
    elif 'LEDU/ETH' == source.pair:
        ticker, orderbook = livecoin_api('LEDU/ETH')
    market.current_price = ticker['last']
    market.lowest_ask = ticker['min_ask']
    market.highest_bid = ticker['max_bid']
    market.save()

    buys = orderbook['bids']
    sells = orderbook['asks']
    for buy in buys:
        order = OrderBook(timestamp=timestamp, source=source, amount=buy[1], rate=buy[0], type=True)
        order.save()
    for sell in sells:
        order = OrderBook(timestamp=timestamp, source=source, amount=sell[1], rate=sell[0], type=False)
        order.save()


def gateio_api(pair):
    ticker = requests.get('https://data.gate.io/api2/1/ticker/' + pair).json()
    orderbook = requests.get('https://data.gate.io/api2/1/orderBook/' + pair).json()
    return ticker, orderbook


@app.task
def gateio_data(timestamp, source_pk, market_pk):
    source = Source.objects.get(id=source_pk)
    market = Market.objects.get(id=market_pk)
    if 'LEDU/BTC' == source.pair:
        ticker, orderbook = gateio_api('ledu_btc')
    elif 'LEDU/ETH' == source.pair:
        ticker, orderbook = gateio_api('ledu_eth')
    market.current_price = ticker['last']
    market.lowest_ask = ticker['lowestAsk']
    market.highest_bid = ticker['highestBid']
    market.save()

    buys = orderbook['bids']
    sells = orderbook['asks']
    for buy in buys:
        order = OrderBook(timestamp=timestamp, source=source, amount=buy[1], rate=buy[0], type=True)
        order.save()
    for sell in sells:
        order = OrderBook(timestamp=timestamp, source=source, amount=sell[1], rate=sell[0], type=False)
        order.save()


def idex_api(pair):
    ticker = requests.get('https://api.idex.market/returnTicker?market=' + pair).json()
    orderbook = requests.get('https://api.idex.market/returnOrderBook?market=' + pair).json()
    return ticker, orderbook


@app.task
def idex_data(timestamp, source_pk, market_pk):
    source = Source.objects.get(id=source_pk)
    market = Market.objects.get(id=market_pk)
    if 'LEDU/ETH' == source.pair:
        ticker, orderbook = idex_api('ETH_LEDU')
    market.current_price = ticker['last']
    market.lowest_ask = ticker['lowestAsk']
    market.highest_bid = ticker['highestBid']
    market.save()

    buys = orderbook['bids']
    sells = orderbook['asks']
    for buy in buys:
        order = OrderBook(timestamp=timestamp, source=source, amount=buy['amount'], rate=buy['price'], type=True)
        order.save()
    for sell in sells:
        order = OrderBook(timestamp=timestamp, source=source, amount=sell['amount'], rate=sell['price'], type=False)
        order.save()


def mercatox_api(pair):
    ticker = requests.get('https://mercatox.com/public/json24full').json()

    scraper = cfscrape.create_scraper(delay=5)
    page_content = scraper.get('https://mercatox.com/exchange/LEDU/'+pair).content
    page_content = page_content.decode()
    content = fromstring(page_content)
    order_book = {}
    sell_amount = content.xpath('//div[@data-stack-action="sell"]/div/div[@class="col-xs-4 amount"]/text()')
    sell_price = content.xpath('//div[@data-stack-action="sell"]/div/div[@class="col-xs-4 price"]/text()')
    asks = []
    for id, a in enumerate(sell_amount):
        asks.append({'amount': a, 'price': sell_price[id]})
    order_book['asks'] = asks

    buy_amount = content.xpath('//div[@data-stack-action="buy" ]/div/div[@class="col-xs-4 amount"]/text()')
    buy_price = content.xpath('//div[@data-stack-action="buy" ]/div/div[@class="col-xs-4 price"]/text()')
    bids = []
    for id, a in enumerate(buy_amount):
        bids.append({'amount': a, 'price': buy_price[id]})
    order_book['bids'] = bids

    return ticker['pairs']['LEDU_' + pair], order_book

@app.task
def mercatox_data(timestamp, source_pk, market_pk):
    source = Source.objects.get(id=source_pk)
    market = Market.objects.get(id=market_pk)
    if 'LEDU/BTC' == source.pair:
        ticker, orderbook = mercatox_api('BTC')
    elif 'LEDU/ETH' == source.pair:
        ticker, orderbook = mercatox_api('ETH')
    market.current_price = ticker['last']
    market.lowest_ask = ticker['lowestAsk']
    market.highest_bid = ticker['highestBid']
    market.save()

    buys = orderbook['bids']
    sells = orderbook['asks']
    for buy in buys:
        order = OrderBook(timestamp=timestamp, source=source, amount=buy['amount'], rate=buy['price'], type=True)
        order.save()
    for sell in sells:
        order = OrderBook(timestamp=timestamp, source=source, amount=sell['amount'], rate=sell['price'], type=False)
        order.save()


@app.task
def scrap_coinmarketcap():
    response = requests.get('https://coinmarketcap.com/currencies/education-ecosystem/')
    t = fromstring(response.text)

    timestamp = time.time()

    markets = t.xpath('//table[@id="markets-table"]/tbody/tr')
    for market in markets:
        name = market.xpath('./td[2]/a/text()')[0]
        pair = market.xpath('./td[3]/a/text()')[0]
        url = market.xpath('./td[3]/a/@href')[0]
        source, created = Source.objects.get_or_create(name=name, pair=pair, url=url)

        data_usd = market.xpath('./td[4]/span/@data-usd')[0]
        data_btc = market.xpath('./td[4]/span/@data-btc')[0]
        data_native = market.xpath('./td[4]/span/@data-native')[0]

        price_usd = market.xpath('./td[5]/span/@data-usd')[0]
        price_btc = market.xpath('./td[5]/span/@data-btc')[0]
        price_native = market.xpath('./td[5]/span/@data-native')[0]

        volume_percent = market.xpath('./td[6]/span/@data-format-value')[0]

        market = Market(timestamp=timestamp, source=source,
                        volume_usd=data_usd, volume_btc=data_btc, volume_native=data_native,
                        price_usd=price_usd, price_btc=price_btc, price_native=price_native,
                        percent=volume_percent)
        market.save()

        if 'Exrates' == source.name:
            exrates_data.delay(timestamp, source.id, market.id)
        elif 'Mercatox' == source.name:
            mercatox_data.delay(timestamp, source.id, market.id)
        elif 'Livecoin' == source.name:
            livecoin_data.delay(timestamp, source.id, market.id)
        elif 'Gate.io' == source.name:
            gateio_data.delay(timestamp, source.id, market.id)
        elif 'IDEX' == source.name:
            idex_data.delay(timestamp, source.id, market.id)
