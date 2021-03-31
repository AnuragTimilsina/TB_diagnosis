from django.conf.urls import url
from django.urls import path
from .views import MyTokenObtainPairView, RegisterView, Image, \
                 changePasswordView, UpdateProfileView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    url(r'^image/$', Image.as_view(), name='upload-image'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('change_password/<int:pk>/', changePasswordView.as_view(), name='auth_change_password'),
    path('update_profile/<int:pk>/', UpdateProfileView.as_view(), name='auth_update_profile'),
]

