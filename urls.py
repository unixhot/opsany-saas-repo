# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^account/', include('blueapps.account.urls')),
    url(r'^', include('index.urls')),
    url(r'^api/repo/v0_1/', include('repo.urls')),
    url(r'^api/repo/esb/v0_1/', include('repo.esb_urls')),
]
