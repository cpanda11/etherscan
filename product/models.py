import requests
import time
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils.translation import gettext_lazy as _
from lxml.html import fromstring

from product.utils import humanize_number


def get_exchange(address):
    address_url = 'https://etherscan.io/address/{address}'.format

    while True:
        try:
            res = requests.get(address_url(address=address))
            if res.text.__contains__('Sorry, You have reached your maximum request limit for this resource.')\
                    or res.status_code != 200:
                print(address, res.status_code)
                time.sleep(1)
                continue
            break
        except:
            time.sleep(1)
            pass
    t = fromstring(res.text)
    exchange = t.xpath('//font[@title="NameTag"]/text()')
    print(address, res.status_code, exchange)
    return exchange[0] if exchange else None


class Address(models.Model):
    address = models.CharField(verbose_name=_('Address'), max_length=42, unique=True)
    is_company = models.BooleanField(verbose_name=_('Company Token'), default=False)
    exchange = models.CharField(verbose_name=_('Exchange'), max_length=60, null=True, blank=True)

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses with LEDU')

    def __str__(self):
        return self.address

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.exchange = get_exchange(self.address)
        super(Address, self).save(force_insert, force_update, using, update_fields)


class Holder(models.Model):
    timestamp = models.DateField(verbose_name=_('Date'), null=True, blank=True)
    rank = models.IntegerField(verbose_name=_('Rank'), null=True, blank=True)
    address = models.ForeignKey(Address, verbose_name=_('Address'), related_name='holder_address',
                                on_delete=models.CASCADE)
    quantity = models.FloatField(verbose_name=_('Current Quantity(Token)'), default=0)
    percentage = models.FloatField(verbose_name=_('Current Percentage'), default=0)
    prev_quantity = models.FloatField(verbose_name=_('Previous Quantity(Token)'), default=0)
    prev_percentage = models.FloatField(verbose_name=_('Previous Percentage'), default=0)
    change = models.FloatField(verbose_name=_('Change'), default=0)

    class Meta:
        verbose_name = _('Holder')
        verbose_name_plural = _('Tracking LEDU Holders')
        ordering = ['pk']

    def __str__(self):
        return str(self.timestamp) + '-' + self.address.address

    def _quantity(self):
        return humanize_number(self.quantity)
    _quantity.short_description = _('Current Quantity(Token)')

    def _percentage(self):
        return str(self.percentage) + '%'
    _percentage.short_description = _('Current Percentage')

    def _prev_quantity(self):
        return humanize_number(self.prev_quantity) if self.change else ''
    _prev_quantity.short_description = _('Previous Quantity(Token)')

    def _prev_percentage(self):
        return str(self.percentage) + '%' if self.change else ''
    _prev_percentage.short_description = _('Previous Percentage')

    def _change(self):
        return (humanize_number(self.change) if self.change else '0') + '%'
    _change.short_description = _('Change')


class Transaction(models.Model):
    hash = models.CharField(verbose_name=_('Hash'), max_length=66)
    _from = models.ForeignKey(Address, verbose_name=_('From'), related_name='tx_from_address', on_delete=models.CASCADE,
                              null=True, blank=True)
    _to = models.ForeignKey(Address, verbose_name=_('To'), related_name='tx_to_address', on_delete=models.CASCADE,
                            null=True, blank=True)
    timestamp = models.DateTimeField(verbose_name=_('TimeStamp'), null=True, blank=True)
    quantity = models.FloatField(verbose_name=_('Quantity'), default=0)

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('All LEDU Transactions')
        unique_together = ['hash', '_from', '_to', 'timestamp', 'quantity']

    def __str__(self):
        return str(self.timestamp) + '-' + self.hash


class Mover(Transaction):
    class Meta:
        proxy = True
        verbose_name = _('Mover')
        verbose_name_plural = _('Tracking LEDU Transaction to Exchange sites')


class Tracking(Transaction):
    class Meta:
        proxy = True
        verbose_name = _('Tracking')
        verbose_name_plural = _('Tracking LEDU Transaction History')
