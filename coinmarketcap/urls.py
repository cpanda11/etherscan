from django.conf.urls import url

from coinmarketcap.views import *


urlpatterns = [
    url(r'^scrap/', scrap),
]
