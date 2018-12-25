import datetime

from django.contrib import admin
from django.utils.safestring import mark_safe

from coinmarketcap.models import *


class BaseAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_continue'] = False
        return admin.ModelAdmin.change_view(self, request, object_id, form_url, extra_context=extra_context)


class SourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'pair', 'url']


class MarketAdmin(BaseAdmin):
    list_display = ['_timestamp', '_source', '_pair', 'volume_usd', 'price_usd', 'percent', '_highest_bid',
                    '_current_price', '_lowest_ask', '_delta_absolute', '_delta_ratio']
    list_filter = ['timestamp', 'source__name', 'source__pair']

    def get_queryset(self, request):
        qs = admin.ModelAdmin.get_queryset(self, request)
        ids = qs.order_by('-timestamp').values_list('pk', flat=True)[:9]
        return qs.filter(pk__in=list(ids)).order_by('-volume_usd')

    def _timestamp(self, obj):
        return datetime.datetime.fromtimestamp(obj.timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def _source(self, obj):
        return obj.source.name

    def _pair(self, obj):
        return obj.source.pair

    def _current_price(self, obj):
        return "{:.9f}".format(obj.current_price)
    _current_price.short_description = 'Current Price'

    def _lowest_ask(self, obj):
        return "{:.9f}".format(obj.lowest_ask)
    _lowest_ask.short_description = 'Lowest Sell Order Price'

    def _delta_absolute(self, obj):
        return "{:.9f}".format(obj.current_price - obj.lowest_ask)
    _delta_absolute.short_description = 'Delta Absolute'

    def _delta_ratio(self, obj):
        ratio = abs(obj.current_price - obj.lowest_ask) * 100
        ratio = ratio / obj.current_price if obj.current_price else 0.0
        if obj.current_price < obj.lowest_ask: ratio = -ratio
        return "{:.2f}".format(ratio) + '%'
    _delta_ratio.short_description = 'Delta %'

    def _highest_bid(self, obj):
        return "{:.9f}".format(obj.highest_bid)

    # def view_buy_orderbook(self, obj):
    #     url = '/coinmarketcap/orderbook/?source__id__exact={id}&type={type}&timestamp={timestamp}'.format
    #     return mark_safe('<a href={orderbook_link}>View Buy OrderBook</span>'.format(
    #         orderbook_link=url(id=obj.source.id, type=True, timestamp=obj.timestamp)))
    #
    # def view_sell_orderbook(self, obj):
    #     url = '/coinmarketcap/orderbook/?source__id__exact={id}&type={type}&timestamp={timestamp}'.format
    #     return mark_safe('<a href={orderbook_link}>View Sell OrderBook</span>'.format(
    #         orderbook_link=url(id=obj.source.id, type=False, timestamp=obj.timestamp)))


class MarketDataTrackingAdmin(MarketAdmin):
    list_display = ['_timestamp', '_source', '_pair', 'volume_usd', 'price_usd', 'percent', '_current_price',
                    '_lowest_ask', 'view_buy_orderbook', 'view_sell_orderbook']
    list_filter = ['timestamp', 'source__name', 'source__pair']

    def get_queryset(self, request):
        qs = admin.ModelAdmin.get_queryset(self, request)
        ids = qs.order_by('-timestamp').values_list('pk', flat=True)[:9]
        return qs.filter(pk__in=list(ids)).order_by('-volume_usd')

    def _timestamp(self, obj):
        return datetime.datetime.fromtimestamp(obj.timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def _source(self, obj):
        return obj.source.name

    def _pair(self, obj):
        return obj.source.pair

    def _current_price(self, obj):
        return "{:.9f}".format(obj.current_price)

    def _lowest_ask(self, obj):
        return "{:.9f}".format(obj.lowest_ask)

    _lowest_ask.short_description = 'Lowest Sell Order Price'

    def _highest_bid(self, obj):
        return "{:.9f}".format(obj.highest_bid)

    def view_buy_orderbook(self, obj):
        url = '/coinmarketcap/orderbook/?source__id__exact={id}&type={type}&timestamp={timestamp}'.format
        return mark_safe('<a href={orderbook_link}>View Buy OrderBook</span>'.format(
            orderbook_link=url(id=obj.source.id, type=True, timestamp=obj.timestamp)))

    def view_sell_orderbook(self, obj):
        url = '/coinmarketcap/orderbook/?source__id__exact={id}&type={type}&timestamp={timestamp}'.format
        return mark_safe('<a href={orderbook_link}>View Sell OrderBook</span>'.format(
            orderbook_link=url(id=obj.source.id, type=False, timestamp=obj.timestamp)))


class OrderBookAdmin(BaseAdmin):
    list_display = ['_timestamp', '_source', '_pair', 'amount', '_rate', '_type']

    def _timestamp(self, obj):
        return datetime.datetime.fromtimestamp(obj.timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def _source(self, obj):
        return obj.source.name

    def _pair(self, obj):
        return obj.source.pair

    def _type(self, obj):
        return 'Buy' if obj.type else 'Sell'

    def _rate(self, obj):
        return "{:.9f}".format(obj.rate)


admin.site.register(Source, SourceAdmin)
admin.site.register(Market, MarketAdmin)
admin.site.register(MarketDataTracking, MarketDataTrackingAdmin)
admin.site.register(OrderBook, OrderBookAdmin)
