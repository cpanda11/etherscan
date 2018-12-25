from django.db import models
from django.utils.translation import gettext_lazy as _


class Source(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=32)
    pair = models.CharField(verbose_name=_('Pair'), max_length=8)
    url = models.URLField(verbose_name=_('Url'))

    class Meta:
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')
        ordering = ['pk']

    def __str__(self):
        return self.name + '-' + self.pair


class Market(models.Model):
    timestamp = models.FloatField()
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    volume_usd = models.FloatField(verbose_name=_('Volume USD(24h)'))
    volume_btc = models.FloatField(verbose_name=_('Volume BTC(24h)'))
    volume_native = models.FloatField(verbose_name=_('Volume Native(24h)'))
    price_usd = models.FloatField(verbose_name=_('Price USD'))
    price_btc = models.FloatField(verbose_name=_('Price BTC'))
    price_native = models.FloatField(verbose_name=_('Price Native'))
    percent = models.FloatField(verbose_name=_('Volume(%)'))
    current_price = models.FloatField(verbose_name=_('Current Price'), default=0.0)
    lowest_ask = models.FloatField(verbose_name=_('Lowest Sell Order'), default=0.0)
    highest_bid = models.FloatField(verbose_name=_('Highest Buy Order'), default=0.0)

    class Meta:
        verbose_name = _('Market')
        verbose_name_plural = _('Dashboard for Tracking in tabular format')

    def __str__(self):
        return self.source.name + ' - ' + self.source.pair


class MarketDataTracking(Market):
    class Meta:
        proxy = True
        verbose_name = _('MarketDataTracking')
        verbose_name_plural = _('LEDU Coin Exchange Data Tracking')


class OrderBook(models.Model):
    timestamp = models.FloatField()
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    amount = models.FloatField(verbose_name=_('Amount'))
    rate = models.FloatField(verbose_name=_('Price'))
    type = models.BooleanField(verbose_name=_('Order Type'))
