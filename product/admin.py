from django.db.models import Q, F, Func
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.utils.safestring import mark_safe

from jet.filters import DateRangeFilter

from product.models import *
from product.filters import ChangeFilter, YearFilter, WeekFilter


class BaseAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        return admin.ModelAdmin.change_view(self, request, object_id, form_url, extra_context=extra_context)


class HolderAdmin(BaseAdmin):
    list_display = ['rank', '_address', 'timestamp', '_prev_quantity', '_prev_percentage',
                    '_quantity', '_percentage', '_change', 'difference']
    list_filter = (ChangeFilter, YearFilter, WeekFilter, ('timestamp', DateRangeFilter), 'timestamp')
    search_fields = ['timestamp', 'address__address', 'quantity']
    list_display_links = None

    def _address(self, obj):
        if Address.objects.filter(is_company=True).filter(address=obj.address.address).exists():
            return mark_safe('<a href={token_link} style="color: red;">{address}</span>'.format(
                token_link='https://etherscan.io/token/0x5b26c5d0772e5bbac8b3182ae9a13f9bb2d03765?a=' + obj.address.address,
                address=obj.address.address
            ))
        else:
            return mark_safe('<a href={token_link}>{address}</span>'.format(
                token_link='https://etherscan.io/token/0x5b26c5d0772e5bbac8b3182ae9a13f9bb2d03765?a=' + obj.address.address,
                address=obj.address.address
            ))
    _address.short_description = 'Address'

    def get_queryset(self, request):
        qs = admin.ModelAdmin.get_queryset(self, request)
        qs = qs.annotate(diff=Func(F('quantity') - F('prev_quantity'), function='ABS'))
        change = request.GET.get('change', '')
        if change and change == 'all':
            return qs
        return qs.filter(Q(change__gt=0) | Q(change__lt=0))

    def difference(self, obj):
        return humanize_number(obj.diff)
    difference.short_description = _('Difference')
    difference.admin_order_field = 'diff'


class TransactionAdmin(BaseAdmin):
    list_display = ['tx_hash', 'from_address', 'to_address', 'timestamp', '_value']
    list_filter = (YearFilter, WeekFilter, ('timestamp', DateRangeFilter))
    search_fields = ['hash', '_from__address', '_to__address']

    def get_queryset(self, request):
        qs = admin.ModelAdmin.get_queryset(self, request)
        qs = qs.extra(select={"custom_dt": "date(timestamp)"}).order_by("-custom_dt", "-quantity")
        return qs

    def tx_hash(self, obj):
        return mark_safe('<a href={hash_link}>{hash}</span>'.format(
            hash_link='https://ethplorer.io/tx/' + obj.hash, hash=obj.hash))
    tx_hash.short_description = 'Hash'

    def from_address(self, obj):
        if Address.objects.filter(is_company=True).filter(address=obj._from.address).exists():
            return mark_safe('<span style="color: red;">{addr}</span>'.format(addr=obj._from.address))
        else:
            return obj._from.address
    from_address.short_description = 'From'

    def to_address(self, obj):
        if Address.objects.filter(is_company=True).filter(address=obj._to.address).exists():
            return mark_safe('<span style="color: red;">{addr}</span>'.format(addr=obj._to.address))
        else:
            return obj._to.address
    to_address.short_description = 'To'

    def _value(self, obj):
        return humanize_number(obj.quantity)
    _value.short_description = _('Quantity')
    _value.admin_order_field = 'quantity'


class TrackingAdmin(BaseAdmin):
    list_display = ['tx_hash', 'from_address', 'to_address', 'timestamp', '_value', 'volume']
    search_fields = ['_from__address', '_to__address']
    address = ''
    volumes = dict()

    def get_queryset(self, request):
        q = request.GET.get('q', '')
        if q:
            q = q.strip()
            if 42 == len(q):
                self.address = q
                qs = Tracking.objects.filter(Q(_from__address=q) | Q(_to__address=q)).order_by('timestamp')
                current_volume = 0.0
                for tracking in qs:
                    if tracking._from.address == q:
                        current_volume -= tracking.quantity
                    else:
                        current_volume += tracking.quantity
                    self.volumes[tracking.id] = current_volume
                return qs
        else:
            return Tracking.objects.none()

    def tx_hash(self, obj):
        return mark_safe('<a href={hash_link}>{hash}</span>'.format(
            hash_link='https://ethplorer.io/tx/' + obj.hash, hash=obj.hash))
    tx_hash.short_description = 'Hash'

    def from_address(self, obj):
        if obj._from.address == self.address:
            return mark_safe('<span style="color: red;">{addr}</span>'.format(addr=obj._from.address))
        else:
            return obj._from.address
    from_address.short_description = 'From'

    def to_address(self, obj):
        if obj._to.address == self.address:
            return mark_safe('<span style="color: red;">{addr}</span>'.format(addr=obj._to.address))
        else:
            return obj._to.address
    to_address.short_description = 'To'

    def _value(self, obj):
        return humanize_number(obj.quantity)
    _value.short_description = _('Quantity')
    _value.admin_order_field = 'quantity'

    def volume(self, obj):
        return humanize_number(self.volumes[obj.id])
    volume.short_description = _('Volume')


class AddressAdmin(BaseAdmin):
    list_display = ['address', 'is_company', 'exchange']
    list_filter = ['is_company', 'exchange']
    search_fields = ['address']


class MoverAdmin(TransactionAdmin):
    list_display = ['timestamp', 'from_address', 'from_exchange', 'to_address', 'to_exchange', '_value', '_percentage']
    list_filter = (YearFilter, WeekFilter, ('timestamp', DateRangeFilter))
    search_fields = ['_from__address', '_to__address']
    list_display_links = None

    def from_address(self, obj):
        return mark_safe('<a href={hash_link}>{address}</span>'.format(
            hash_link='https://etherscan.io/tx/' + obj.hash, address=obj._from.address,))
    from_address.short_description = 'From Address'

    def to_address(self, obj):
        return mark_safe('<a href={hash_link}>{address}</span>'.format(
            hash_link='https://ethplorer.io/tx/' + obj.hash, address=obj._to.address,))
    to_address.short_description = 'To Address'

    def from_exchange(self, obj):
        return obj._from.exchange
    from_exchange.admin_order_field = '_from__exchange'
    from_exchange.short_description = 'From Exchange'

    def to_exchange(self, obj):
        return obj._to.exchange
    to_exchange.admin_order_field = '_from__exchange'
    to_exchange.short_description = 'To Exchange'

    def _value(self, obj):
        return humanize_number(obj.quantity)
    _value.admin_order_field = 'quantity'
    _value.short_description = _('Ledu Volume Moved')

    def _percentage(self, obj):
        return '%.9f' % obj.percentage + '%'
    _percentage.admin_order_field = 'percentage'
    _percentage.short_description = _('Percentage')

    def get_queryset(self, request):
        qs = admin.ModelAdmin.get_queryset(self, request)
        qs = qs.filter(quantity__gt=0)
        qs = qs.annotate(percentage=F('quantity') / 3629830.9430186835)
        qs = qs.order_by('-timestamp')
        return qs


admin.site.register(Address, AddressAdmin)
admin.site.register(Holder, HolderAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Tracking, TrackingAdmin)
admin.site.register(Mover, MoverAdmin)
admin.site.site_header = 'LEDU Statistics'
