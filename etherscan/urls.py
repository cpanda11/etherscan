"""etherscan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.shortcuts import redirect
from django.urls import path
from django.contrib import admin
from django.conf.urls.static import static
from django.utils import translation

from etherscan import settings


def switch_language(request, language):
    translation.activate(language)
    request.session[translation.LANGUAGE_SESSION_KEY] = language
    return redirect('/')


urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),

    url(r'^', admin.site.urls),

    url(r'^rosetta/', include('rosetta.urls')),

    path('i18n/', include('django.conf.urls.i18n')),
    path('language/<language>/', switch_language),

    url(r'^product/', include('product.urls')),
    url(r'^coinmarketcap/', include('coinmarketcap.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
