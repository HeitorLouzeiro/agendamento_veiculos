from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('cursos/', include('cursos.urls')),
    path('veiculos/', include('veiculos.urls')),
    path('agendamentos/', include('agendamentos.urls')),
]
