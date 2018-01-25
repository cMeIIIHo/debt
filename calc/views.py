import datetime
import calendar
from calc.models import *
from django.shortcuts import render
from django.db.models import Sum
from django.http import Http404


def show_accounts(request):
    return render(request, 'calc/index.html', {'accounts': Account.objects.all()})


def show_accruals(request, account_id):
    account = Account.objects.get(pk=account_id)

    debet = account.debet_set.aggregate(debet=Sum('amount'))
    credit = account.credit_set.aggregate(debet=Sum('amount'))
    if debet != credit:
        raise Http404('debet != credit')

    start = account.debet_set.first().date
    end = account.credit_set.last().date
    rate = account.percent_rate
    day = account.percent_pay_day

    def get_first_accrual_date(start, day):
        """
        В зависимоти от сочетания выбранных числа начисления, первого поступления долга, и дней в этом месяце,
        определяет первую дату начисления, от нее удобнее отталкиваться
        """

        if start.day < day <= calendar.monthrange(start.year, start.month)[1]:
            date = datetime.date(start.year, start.month, day)
            accrual_dates.append(date)
        elif start.day <= calendar.monthrange(start.year, start.month)[1] < day:
            date = datetime.date(start.year, start.month, calendar.monthrange(start.year, start.month)[1])
            accrual_dates.append(date)
        else:
            date = datetime.date(start.year, start.month, day)
        return date

    def get_next_accrual_date(date, day):
        """
        вычисляет следующую дату начисления, отталкиваясь от предыдущей,
        контролирует переход на следующий год если прошел последний месяц
        """
        month = date.month
        year = date.year
        if month < 12:
            month += 1
        else:
            month = 1
            year += 1
        if day > calendar.monthrange(year, month)[1]:
            day = calendar.monthrange(year, month)[1]
        return datetime.date(year, month, day)

    def get_all_accrual_dates(start, end, day):
        """
        вычисляет все даты начисления и заносит их в список accrual_dates
        """
        first_accrual_date = get_first_accrual_date(start, day)
        prev_accrual_date = first_accrual_date
        while True:
            next_accrual_date = get_next_accrual_date(prev_accrual_date, day)
            if next_accrual_date < end:
                accrual_dates.append(next_accrual_date)
                prev_accrual_date = next_accrual_date
            else:
                accrual_dates.append(end)
                break

    def get_account_events():
        """
        finds all events that happened with account - rise/reduce debt - and store it like
        {date:[event1, event2...]}
        """
        for debet in account.debet_set.all():
            account_events[debet.date] = account_events.get(debet.date, [])
            account_events[debet.date].append(debet.amount)

        for credit in account.credit_set.all():
            account_events[credit.date] = account_events.get(credit.date, [])
            account_events[credit.date].append(-credit.amount)

    def get_all_accruals(account_events, accrual_dates):
        """
        цикл, проходя по всем датам долгаv, сравнивает дату с датами в массивах, получая представление о хронологии событий
        и о самих событиях, согласно которым вносит изменения в переменные, хранящие состояние. Печатает выплаты.
        """
        percent_to_pay_this_month = 0
        balance = 0
        today = start
        for i in range((end - today).days):
            if today in account_events:
                for event in account_events[today]:
                    balance += event
            today = today + datetime.timedelta(days=1)
            if calendar.isleap(today.year):
                days_in_year = 366
            else:
                days_in_year = 365
            percent_to_pay_this_day = balance * rate / days_in_year
            percent_to_pay_this_month += percent_to_pay_this_day
            if today in accrual_dates:
                accruals[today] = percent_to_pay_this_month
                percent_to_pay_this_month = 0

    accrual_dates = []
    get_all_accrual_dates(start, end, day)

    account_events = {}
    get_account_events()

    accruals = {}
    get_all_accruals(account_events, accrual_dates)

    return render(request, 'calc/index.html', {'accruals': accruals})




