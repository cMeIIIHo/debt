from django.db import models


class Account(models.Model):
    number = models.IntegerField()
    percent_rate = models.FloatField(blank=True, null=True)
    percent_pay_day = models.IntegerField(blank=True, null=True)


class Debet(models.Model):

    class Meta:
        ordering = ['date']

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return '%s - %s - %s' % (self.account.number, self.amount, self.date, )


class Credit(models.Model):

    class Meta:
        ordering = ['date']

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return '%s - %s - %s' % (self.account.number, self.amount, self.date,)
