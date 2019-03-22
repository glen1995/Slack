from django.conf.urls import url
from votingapp import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^vote$', views.vote, name='vote'),
    url(r'^play/$', views.play, name='play'),
]