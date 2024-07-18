from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
import base64


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, password=None, is_admin=False, is_active=False,):
        if not email:
            raise ValueError('O email é obrigatório.')

        if not nome:
            raise ValueError('O nome é obrigatório.')

        user = self.model(
            email=self.normalize_email(email),
            nome=nome,
        )
        user.set_password(password)
        user.is_admin = is_admin
        user.is_active = is_active
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password):
        user = self.create_user(
            email=email,
            nome=nome,
            password=password,
            is_admin=True,
            is_active=True
        )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    idade = models.PositiveIntegerField(blank=True, null=True)
    foto_perfil = models.TextField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'password', 'telefone']

    class Meta:
        verbose_name_plural = 'usuarios'
        db_table = 'usuario'
        verbose_name = 'usuario'
        ordering = ['-created_at']  # created_at do mais recente

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if self.foto_perfil:
            self.foto = base64.b64encode(self.foto_perfil.encode()).decode('utf-8')
        super().save(*args, **kwargs)

    def get_by_natural_key(self, email):
        return self.get(email=email)

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def create_superuser(self, email, nome, password=None):
        user = self.create_user(
            email=email,
            nome=nome,
            senha=password,
            is_admin=True,
            is_active=True
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class Animal(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='animais')
    nome = models.CharField(max_length=100)
    idade = models.PositiveIntegerField(blank=True, null=True)
    especie = models.CharField(max_length=100, blank=False, null=True)
    raca = models.CharField(max_length=100, blank=True, null=True)
    cor = models.CharField(max_length=100, blank=True, null=True)
    foto_pet = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=False)  # Falso = com o dono/ True = com o pet_shop
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'animais'
        verbose_name = 'animal'
        verbose_name_plural = 'animais'
        ordering = ['nome']

    def save(self, *args, **kwargs):
        if self.foto_pet:
            self.foto = base64.b64encode(self.foto_pet.encode()).decode('utf-8')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
