from django.db import models
from django.utils.translation import gettext_lazy as _


class Account(models.Model):
    email = models.EmailField(verbose_name=_('Email'), max_length=100)
    email_password = models.CharField(verbose_name=_('Email Password'), max_length=30)
    bitforex_password = models.CharField(verbose_name=_('Bitforex Password'), max_length=30)
    access_key = models.CharField(verbose_name=_('Access Key'), max_length=31, null=True, blank=True)
    secret_key = models.CharField(verbose_name=_('Secret Key'), max_length=32, null=True, blank=True)

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')
        ordering = ['pk']

    def __str__(self):
        return self.email

    def e_password(self):
        return '*' * len(self.email_password)

    def b_password(self):
        return '*' * len(self.bitforex_password)
