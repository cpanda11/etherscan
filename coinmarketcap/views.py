from django.shortcuts import redirect

from coinmarketcap.tasks import scrap_coinmarketcap


def scrap(request):
    scrap_coinmarketcap.delay()

    return redirect('/coinmarketcap/market/')
