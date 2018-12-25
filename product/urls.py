from django.conf.urls import url

from product.views import *


urlpatterns = [
    url(r'^scrap/', scrap),
]
