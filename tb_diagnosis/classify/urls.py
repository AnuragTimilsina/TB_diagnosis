from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('',views.home,name="home"),
    path('index', views.index, name='index'),
    path('signin',views.Sign_In,name='signin'),
    path('signup',views.Sign_Up,name='signup'),
    path('logout',views.logout,name='logout'),
    url('predictImage', views.predictImage, name='predictImage'),
    url('report/<int:id>/',views.Get_Report,name='report'),
    #url('viewDataBase', views.viewDataBase, name='viewDatabase'),
]
