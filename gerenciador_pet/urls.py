from django.contrib import admin
from django.core.management import call_command
from django.shortcuts import redirect
from django.urls import path, include
from django.db import connection

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pet_shop/', include('pet_shop.urls')),
    path('', lambda request: redirect('pet_shop/', permanent=True))
]


# Verifica se a tabela usuario já existe antes de tentar criar superusuario
def existe_tabela(nome_tabela):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            )
        """, [nome_tabela])
        return cursor.fetchone()[0]


if existe_tabela('usuario'):
    try:
        call_command('criar_superusuario_se_nao_existir')
    except Exception as e:
        print(f"Erro ao criar superusuário: {e}")
else:
    print("A tabela 'usuario' não existe. Não é possível criar o superusuário.")
