from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('cursos/', include('cursos.urls')),
    path('veiculos/', include('veiculos.urls')),
    path('agendamentos/', include('agendamentos.urls')),
]
