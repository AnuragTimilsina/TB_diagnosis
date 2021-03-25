from django.conf.urls import url
from .views import Image

urlpatterns = [
    url(r'^image/$', Image.as_view(), name='upload-image'),
]
