import re
import datetime
from time import strptime, strftime


def get_week_details(year, week_no, week_start=2):
    janOne = strptime('%s-01-01' % year, '%Y-%m-%d')
    dayOfFirstWeek = ((7 - int((strftime("%u", janOne))) + int(week_start)) % 7)
    if dayOfFirstWeek == 0:
        dayOfFirstWeek = 7
    dateOfFirstWeek = strptime('%s-01-%s' % (year, dayOfFirstWeek), '%Y-%m-%d')
    dayOne = datetime.datetime(dateOfFirstWeek.tm_year, dateOfFirstWeek.tm_mon, dateOfFirstWeek.tm_mday)
    daysToGo = 7*(int(week_no)-1)
    lastDay = daysToGo+6
    dayX = dayOne + datetime.timedelta(days=daysToGo)
    dayY = dayOne + datetime.timedelta(days=lastDay)
    resultDateX = strptime('%s-%s-%s' % (dayX.year, dayX.month, dayX.day), '%Y-%m-%d')
    resultDateY = strptime('%s-%s-%s' % (dayY.year, dayY.month, dayY.day), '%Y-%m-%d')
    return str(datetime.datetime(*resultDateX[:6]).date()) + ' ~ ' + str(datetime.datetime(*resultDateY[:6]).date())


def humanize_number(value):
    if value < 0.0:
        value = '%.8f' % value
        value = value[1:]
        value = str(value).split('.')
        return '-' + ','.join(re.findall('.{1,3}', value[0][::-1]))[::-1] + '.' + value[1]
    elif value > 0.0:
        value = '%.8f' % value
        value = str(value).split('.')
        return ','.join(re.findall('.{1,3}', value[0][::-1]))[::-1] + '.' + value[1]
    else:
        return '0'


if __name__ == '__main__':
    WeekData = get_week_details(2017, 1)
    print("Monday of Week %s: %s \n" % (2018, str(WeekData[0])))
    print("Sunday of Week %s: %s \n" % (2018, str(WeekData[1])))
