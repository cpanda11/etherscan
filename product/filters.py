import datetime
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from product.utils import get_week_details


class ChangeFilter(admin.SimpleListFilter):
    title = _('Change')
    parameter_name = 'change'

    def lookups(self, request, model_admin):
        return (
            ('all', _('All')),
            ('positive', _('Positive')),
            ('negative', _('Negative')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'positive':
            return queryset.filter(change__gt=0)
        elif self.value() == 'negative':
            return queryset.filter(change__lt=0)
        return queryset


class YearFilter(admin.SimpleListFilter):
    title = _('Year')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        years = sorted(list(set([a.year for a in list(model_admin.model.objects.values_list('timestamp', flat=True))])))
        return tuple([(year, year) for year in years])

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(timestamp__year=self.value())


class WeekFilter(admin.SimpleListFilter):
    title = _('Week')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'week'

    def lookups(self, request, model_admin):
        number_of_weeks = datetime.date(datetime.datetime.now().year, 12, 28).isocalendar()[1]
        weeks = []
        for week in range(number_of_weeks):
            start_end = get_week_details(datetime.datetime.now().year, week + 1)
            weeks.append((start_end, 'Week %s, %s' % (str(week + 1), start_end)))
        return tuple(weeks)

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        start_date = datetime.datetime.strptime(self.value().split(' ~ ')[0], '%Y-%m-%d')
        end_date = datetime.datetime.strptime(self.value().split(' ~ ')[1], '%Y-%m-%d')
        return queryset.filter(timestamp__gte=start_date).filter(timestamp__lte=end_date)
