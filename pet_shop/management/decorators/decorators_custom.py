from django.shortcuts import redirect

from django.contrib import messages


# Verifica a autenticação
def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Permições insuficientes.')
            return redirect('login')

    return wrapper


# Verifica se usuario é admin
def admin_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Permições insuficientes.')
            return redirect('dashboard')

    return wrapper


# Redireciona caso usuario ja esteja logado
def redirect_authenticated_user(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)

    return wrapper