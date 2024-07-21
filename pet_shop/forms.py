from django import forms
from pet_shop.models import Usuario, Animal
from django.contrib.auth import authenticate


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UsuarioForm(BootstrapModelForm):
    foto_perfil = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control',
        'accept': 'image/*'
    }))

    class Meta:
        model = Usuario
        fields = ['nome', 'idade', 'email', 'password', 'telefone', 'foto_perfil']
        widgets = {
            'password': forms.PasswordInput(),
            'telefone': forms.TextInput(attrs={'data-mask': '(00)00000-0000'}),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario


class PetForm(BootstrapModelForm):
    foto_pet = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control-file',
        'accept': 'image/*'
    }))

    class Meta:
        model = Animal
        fields = ['nome', 'idade', 'especie', 'raca', 'cor', 'foto_pet']
        labels = {
            'nome': 'Nome',
            'idade': 'Idade',
            'especie': 'Espécie',
            'raca': 'Raça',
            'cor': 'Cor',
            'foto_pet': 'Foto',
        }
        widgets = {
            'especie': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Escolha a espécie do animal',
            }),
        }


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Digite seu email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Digite sua senha'
    }))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                usuario = authenticate(username=email, password=password)
                if usuario is None:
                    raise forms.ValidationError('Senha incorreta.')
            except Usuario.DoesNotExist:
                raise forms.ValidationError('Email não encontrado.')

        return cleaned_data


class AtualizarDadosForm(forms.ModelForm):
    old_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Sua senha'
    }))

    new_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Nova senha'
    }))

    confirm_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirmar nova senha'
    }))

    foto_perfil = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control',
        'accept': 'image/*'
    }))

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'idade', 'telefone', 'foto_perfil', 'old_password', 'new_password',
                  'confirm_password']
        widgets = {
            'nome':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'idade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Idade'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'data-mask': '(00)00000-0000'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if confirm_password and new_password and confirm_password != new_password:
            raise forms.ValidationError({'confirm_password': 'As senhas não coincidem.'})

        elif new_password and old_password and new_password == old_password:
            raise forms.ValidationError({'new_password': 'A nova senha não pode ser igual à antiga.'})

        return cleaned_data
