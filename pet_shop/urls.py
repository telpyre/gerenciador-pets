from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.cadastrar_usuario, name='novo_usuario'),
    path('ativar/<uidb64>/<token>', views.ativar_usuario, name='ativar_usuario'),
    path('reenviar_email_ativacao/<int:usuario_id>', views.reenviar_email_ativacao, name='reenviar_email_ativacao'),
    path('login/', views.login, name='login'),
    path('', views.dashboard, name='dashboard'),
    path('pet/adicionar/', views.adicionar_pet, name='adicionar_pet'),
    path('pet/listar/', views.listar_pets, name='listar_pets'),
    path('pet/status/recebido', views.pet_status_recebido, name='status_pet_recebido'),
    path('pet/status/devolvido', views.pet_status_devolvido, name='status_pet_devolvido'),
    path('pet/editar/<int:animal_id>', views.editar_pet, name='editar_pet'),
    path('pet/excluir/<int:animal_id>', views.excluir_pet, name='excluir_pet'),
    path('usuario/atualizar_dados', views.atualizar_dados, name='atualizar_dados'),
    path('admin/usuarios/listar/', views.listar_usuarios, name='listar_usuarios'),
    path('admin/usuarios/desativar/<int:usuario_id>/', views.desativar_usuario, name='desativar_usuario'),
    path('admin/usuarios/reativar/<int:usuario_id>/', views.ativar_usuario, name='ativar_usuario'),
    path('admin/usuarios/excluir/<int:usuario_id>/', views.excluir_usuario, name='excluir_usuario'),
    path('logout/', views.logout, name='logout'),
]