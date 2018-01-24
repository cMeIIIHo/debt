import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'debt.settings')
import django
django.setup()

import datetime
import calendar
from calc.models import *

account = Account.objects.get(number=2)           # в базе 2 объекта - которые были на картинке - удобно проверять
                                                  # для выбора из этих двух - укажите номер ( 1 или 2 )

start = account.debet_set.first().date            # самое первое поступление долга
end = account.credit_set.last().date              # самая последняя оплата
rate = account.percent_rate                       # ставка
day = account.percent_pay_day                     # дата начисления процентов


def get_first_checkpoint(start, end, day):
    """
    В зависимоти от сочетания выбранных числа начисления, первого поступления долга, и дней в этом месяце,
    определяет первую дату начисления, от нее удобнее отталкиваться
    """
    if start.day < day <= calendar.monthrange(start.year, start.month)[1]:
        date = datetime.date(start.year, start.month, day)
        checkpoints.append(date)
    elif start.day <= calendar.monthrange(start.year, start.month)[1] < day:
        date = datetime.date(start.year, start.month, calendar.monthrange(start.year, start.month)[1])
        checkpoints.append(date)
    elif day <= start.day:
        date = datetime.date(start.year, start.month, day)
    return date


def get_next_checkpoint(date, day):
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


def get_all_checkpoints(start, end, day):
    """
    вычисляет все даты начисления и заности их в список checkpoints
    """
    first_checkpoint = get_first_checkpoint(start, end, day)
    previous_checkpoint = first_checkpoint
    while True:
        next_checkpoint = get_next_checkpoint(previous_checkpoint, day)
        if next_checkpoint < end:
            checkpoints.append(next_checkpoint)
            previous_checkpoint = next_checkpoint
        else:
            checkpoints.append(end)
            break


# ниже 3 оъекта - список с датами начисления, словарь с датами поступления и словарь с датами погашения долга
# сравнивая данные в них с какой-то датой, можно понять,
# какие события произошли в этот день - было ли изменение долга или начисления
checkpoints = []
get_all_checkpoints(start, end, day)
debets = {debet.date: debet.amount for debet in account.debet_set.all()}
credits = {credit.date: -credit.amount for credit in account.credit_set.all()}


def print_payments(debets, credits, rate):
    """
    цикл, проходя по всем датам долга, сравнивает дату с датами в массивах, получая представление о хронологии событий
    и о самих событиях, согласно которым вносит изменения в переменные, хранящие состояние. Печатает выплаты.
    """
    percent_to_pay_this_month = 0
    balance = 0
    today = start
    for i in range((end-today).days):
        if today in debets:
            balance += debets[today]
        if today in credits:
            balance += credits[today]
        today = today + datetime.timedelta(days=1)
        if calendar.isleap(today.year):
            days_in_year = 366
        else:
            days_in_year = 365
        percent_to_pay_this_day = balance * rate / days_in_year
        percent_to_pay_this_month += percent_to_pay_this_day
        if today in checkpoints:
            print(f'в день {today} начислено {percent_to_pay_this_month}')  # вывод в консоль
            percent_to_pay_this_month = 0


print_payments(debets, credits, rate)




