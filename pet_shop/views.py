from django.contrib.auth.decorators import login_required

from .models import Usuario, Animal
from .forms import UsuarioForm, PetForm, LoginForm, AtualizarDadosForm
from .management.decorators.decorators_custom import login_required_custom, admin_required_custom, \
    redirect_authenticated_user

import base64
import io
from PIL import Image
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib import messages
from django.conf import settings


# ===/views utilitárias/===
def enviar_email_ativacao(request, usuario):
    current_site = get_current_site(request)
    mail_subject = 'Ative sua conta'
    # from_email = 'no-reply@petshopmanager.com'
    recipient_list = [usuario.email]
    message = render_to_string('usuarios/email_ativacao.html', {
        'usuario': usuario,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(usuario.id)),
        'token': default_token_generator.make_token(usuario),
    })
    send_mail(mail_subject, '', settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False, html_message=message)
    usuario.save()


def ativar_usuario(request, uidb64, token):
    try:
        usuario_id = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.defer('password').get(pk=usuario_id)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None

    if usuario is not None and default_token_generator.check_token(usuario, token):
        usuario.is_active = True
        usuario.save()
        messages.success(request, 'Sua conta foi ativada com sucesso.')
        return redirect('login')
    else:
        messages.error(request, 'O link de ativação inválido.')
        return redirect('registro')


def reenviar_email_ativacao(request, usuario_id):
    usuario = Usuario.objects.get(id=usuario_id)
    if usuario:
        if not usuario.is_active:
            enviar_email_ativacao(request, usuario)
            messages.success(request, 'O email de ativação foi reenviado')
        else:
            messages.info(request, 'Este usuário ja esta ativo')
    return redirect('dashboard')


def enviar_email_tutor(request, animal_id):
    pet = Animal.objects.get(id=animal_id)
    usuario = Usuario.objects.get(id=pet.usuario_id)
    current_site = get_current_site(request)
    mail_subject = 'Seu pet está pronto para ser buscado'
    from_email = 'no-reply@petshopmanager.com'
    recipient_list = [usuario.email]
    message = render_to_string('pets/email_buscar_pet.html', {
        'pet': pet,
        'usuario': usuario,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(usuario.id)),
        'token': default_token_generator.make_token(usuario),
    })
    send_mail(mail_subject, '', from_email, recipient_list, fail_silently=False, html_message=message)
    usuario.is_notificado = True
    usuario.save()
    messages.success(request, f'{usuario.nome} foi notificado com sucesso')
    return redirect('listar_pets')


# ===/views para ADMIN/===

@admin_required_custom
def listar_usuarios(request):
    query = request.GET.get('q')
    status = request.GET.get('status')
    idade = request.GET.get('idade')
    usuarios = Usuario.objects.all()
    if query:
        usuarios = usuarios.filter(Q(nome__icontains=query)
                                   | Q(email__icontains=query)
                                   | Q(telefone__icontains=query)
                                   )

    if status:
        is_active = True if status == 'ativo' else False
        usuarios = usuarios.filter(is_active=is_active)

    if idade:
        try:
            idade = int(idade)
            faixa_min = idade - 3
            faixa_max = idade + 3
            usuarios = usuarios.filter(idade__range=(faixa_min, faixa_max))
        except ValueError:
            pass  # Se a idade não for um número, ignorar esse filtro

    usuarios = usuarios.filter(is_admin=False).annotate(num_pets=Count('animais'))
    pets = Animal.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios, 'pets': pets})


@admin_required_custom
def desativar_usuario(request, usuario_id):
    try:
        usuario = get_object_or_404(Usuario, id=usuario_id)
        usuario.is_active = False
        usuario.save()
        messages.success(request, f'Usuário \'{usuario.nome}\' desativado com sucesso.')
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
    return redirect('listar_usuarios')


@admin_required_custom
def reativar_usuario(request, usuario_id):
    try:
        usuario = get_object_or_404(Usuario, id=usuario_id)
        usuario.is_active = True
        usuario.save()
        messages.success(request, f'Usuário \'{usuario.nome}\' reativado com sucesso.')
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
    return redirect('listar_usuarios')


@admin_required_custom
def excluir_usuario(request, usuario_id):
    try:
        usuario = get_object_or_404(Usuario, id=usuario_id)
        usuario.delete()
        messages.success(request, f'Usuário \'{usuario.nome}\' excluído com sucesso.')
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
    return redirect('listar_usuarios')


@admin_required_custom
def pet_status_recebido(request, animal_id):
    try:
        pet = get_object_or_404(Animal, id=animal_id)
        if not pet.status:
            pet.status = True
            pet.save()
            messages.success(request, f'Pet \'{pet.nome}\' foi recebido!')
            return redirect('listar_pets')
        else:
            messages.error(request, f'Pet \'{pet.nome}\' já está conosco.')
    except Usuario.DoesNotExist:
        messages.error(request, 'Pet não encontrado.')
    return redirect('listar_pets')


@admin_required_custom
def pet_status_devolvido(request, animal_id):
    try:
        pet = get_object_or_404(Animal, id=animal_id)
        usuario = get_object_or_404(Usuario, id=pet.usuario)
        if pet.status:
            pet.status = False
            pet.save()
            usuario.is_notificado = False
            usuario.save()
            messages.success(request, f'Pet \'{pet.nome}\' foi devolvido ao dono.')
            return redirect('listar_pets')
        else:
            messages.success(request, f'Pet \'{pet.nome}\' não está conosco.')

    except Usuario.DoesNotExist:
        messages.error(request, 'Pet não encontrado.')
    return redirect('listar_pets')


@admin_required_custom
def listar_pets(request):
    query = request.GET.get('q')
    status = request.GET.get('status')
    dono = request.GET.get('dono')
    pets = Animal.objects.all()
    if query:
        pets = pets.filter(Q(nome__icontains=query) |
                           Q(especie__icontains=query) |
                           Q(raca__icontains=query) |
                           Q(idade__icontains=query) |
                           Q(cor__icontains=query)
                           )

    if status:
        na_loja = True if status == 'true' else False
        pets = pets.filter(status=na_loja)

    if dono:
        pets = pets.filter(usuario__nome__icontains=dono)

    return render(request, 'pets/listar_pets.html', {'pets': pets})


# ===/views para TUTOR/===

@login_required_custom
def dashboard(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.defer('password').get(id=usuario_id)

    if usuario.is_admin:
        pets = Animal.objects.all()
        total_usuarios = Usuario.objects.filter(is_admin=False).count()
        usuarios_ativos = Usuario.objects.filter(is_admin=False, is_active=True).count()
        usuarios_inativos = total_usuarios - usuarios_ativos
        ultimos_usuarios = Usuario.objects.filter(is_admin=False).order_by('-created_at')[:5]

        context = {
            'pets': pets,
            'usuario': usuario,
            'total_usuarios': total_usuarios,
            'usuarios_ativos': usuarios_ativos,
            'usuarios_inativos': usuarios_inativos,
            'ultimos_usuarios': ultimos_usuarios
        }
    else:
        pets = Animal.objects.filter(usuario=usuario)

        context = {
            'usuario': usuario,
            'pets': pets
        }
    return render(request, 'pets/dashboard.html', context)


def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            if 'foto_perfil' in request.FILES:
                imagem = Image.open(request.FILES['foto_perfil'])
                imagem = imagem.resize((300, 300), Image.LANCZOS)
                buffered = io.BytesIO()
                imagem.save(buffered, format='PNG')
                usuario.foto_perfil = base64.b64encode(buffered.getvalue()).decode('utf-8')
            usuario.save()
            enviar_email_ativacao(request, usuario)
            messages.success(request, 'Conta criada com sucesso! Verifique seu email para ativar a conta.')
            return redirect('login')
        else:
            return render(request, 'usuarios/cadastrar_usuario.html', {'form': form})
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/cadastrar_usuario.html', {'form': form})


@redirect_authenticated_user
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                usuario = authenticate(request, username=email, password=password)
                if usuario is not None:
                    if usuario.is_active:
                        request.session['usuario_id'] = usuario.id
                        auth_login(request, usuario)
                        return redirect('dashboard')
                    else:
                        messages.error(request, 'Sua conta não está ativa.')
                else:
                    messages.error(request, 'Email ou senha inválidos.')
            except Usuario.DoesNotExist:
                if Usuario.objects.filter(email=email).exists():
                    messages.error(request, 'Email ou senha inválidos?.')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})


@login_required_custom
def atualizar_dados(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    if request.method == 'POST':
        form = AtualizarDadosForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)

            test_password = form.cleaned_data['old_password']
            if test_password:
                old_password = form.cleaned_data['old_password']
                new_password = form.cleaned_data['new_password']
                confirm_password = form.cleaned_data['confirm_password']
                if new_password != '' and confirm_password != '':
                    if usuario.check_password(old_password):
                        if new_password == confirm_password:
                            usuario.set_password(new_password)
                            usuario.save()
                            update_session_auth_hash(request, usuario)
                        else:
                            form.add_error(None, 'As novas senhas não coincidem')
                            messages.error(request, 'As novas senhas não coincidem')
                            return redirect('atualizar_dados')
                    else:
                        form.add_error('old_password', 'A senha antiga está incorreta')
                        messages.error(request, 'A senha antiga está incorreta')
                        return redirect('atualizar_dados')
                else:
                    form.add_error(None, 'Preencha todos os campos para atualizar a senha.')
                    messages.error(request, 'Preencha todos os campos para atualizar a senha.')
                    return redirect('atualizar_dados')

            usuario.save()
            messages.success(request, f'Dados atualizado com sucesso!')
            return redirect('dashboard')
    else:
        form = AtualizarDadosForm(instance=usuario)
    return render(request, 'usuarios/editar_info.html', {'form': form, 'usuario': usuario})


@login_required_custom
def logout(request):
    auth_logout(request)
    return redirect('login')


@login_required_custom
def adicionar_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.usuario_id = request.session.get('usuario_id')

            if 'foto_pet' in request.FILES:
                foto = request.FILES['foto_pet']
                img = Image.open(io.BytesIO(foto.read()))
                img.thumbnail((300, 300))
                buffered = io.BytesIO()
                img.save(buffered, format='PNG')
                pet.foto_pet = base64.b64encode(buffered.getvalue()).decode('utf-8')

            pet.save()
            messages.success(request, f'Pet \'{pet.nome}\' adicionado com sucesso!')
            return redirect('dashboard')
        else:
            return render(request, 'pets/adicionar_pet.html', {'form': form})
    else:
        form = PetForm()
    return render(request, 'pets/adicionar_pet.html', {'form': form})


@login_required_custom
def editar_pet(request, animal_id):
    pet = get_object_or_404(Animal, id=animal_id, usuario_id=request.session.get('usuario_id'))
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.usuario_id = request.session.get('usuario_id')

            if 'foto_pet' in request.FILES:
                imagem = Image.open(request.FILES['foto_pet'])
                imagem = imagem.resize((300, 300), Image.LANCZOS)
                buffered = io.BytesIO()
                imagem.save(buffered, format='PNG')
                pet.foto_pet = base64.b64encode(buffered.getvalue()).decode('utf-8')

            pet.save()
            messages.success(request, f'Pet \'{pet.nome}\' atualizado com sucesso!')
            return redirect('dashboard')
    else:
        form = PetForm(instance=pet)
    return render(request, 'pets/editar_pet_info.html', {'form': form, 'pet': pet})


@login_required_custom
def excluir_pet(request, animal_id):
    pet = get_object_or_404(Animal, id=animal_id, usuario_id=request.session.get('usuario_id'))
    if request.method == 'POST':
        pet.delete()
        messages.success(request, f'Pet excluído com sucesso!')
        return redirect('dashboard')
    return render(request, 'pets/excluir_pet.html', {'pet': pet})
