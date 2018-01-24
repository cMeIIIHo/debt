from django.contrib import admin
from calc.models import *


class DebetInline(admin.StackedInline):
    model = Debet


class CreditInline(admin.StackedInline):
    model = Credit


class AccountAdmin(admin.ModelAdmin):
    inlines = [
        DebetInline,
        CreditInline
    ]


admin.site.register(Account, AccountAdmin)
