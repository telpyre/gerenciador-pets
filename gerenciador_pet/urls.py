from django.contrib import admin
from django.core.management import call_command
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pet_shop/', include('pet_shop.urls')),
]

call_command('criar_superusuario_se_nao_existir')

