from django.conf.urls import url
from calc import views

app_name = 'calc'


urlpatterns = [
    url(r'^$', views.show_accounts, name='show_accounts'),
    url(r'^account/(?P<account_id>[0-9]+)/$', views.show_accruals, name='show_accruals'),
]