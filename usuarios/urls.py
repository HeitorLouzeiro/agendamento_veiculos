from django.urls import path
from django.views.generic import RedirectView

from .views import CustomLoginView, CustomLogoutView, registro

urlpatterns = [
    path(
        '',
        RedirectView.as_view(pattern_name='login', permanent=False),
        name='home'
    ),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('registro/', registro, name='registro'),
]
