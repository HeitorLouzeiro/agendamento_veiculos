from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('campus/', include('campus.urls')),
    path('cursos/', include('cursos.urls')),
    path('veiculos/', include('veiculos.urls')),
    path('agendamentos/', include('agendamentos.urls')),
    path('frotas/', include('frotas.urls')),
]
