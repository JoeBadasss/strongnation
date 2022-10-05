from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views
from ecom import views as eviews

urlpatterns = [
    path('',eviews.home,name='home')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)