from django.core.management.base import BaseCommand

from pet_shop.models import Usuario


class Command(BaseCommand):
    help = "Cria um superusuário se o mesmo não existir ainda"

    def handle(self, *args, **options):

        if not Usuario.objects.filter(is_admin=True).exists():
            Usuario.objects.create_superuser(
                nome='Admin',
                email='admin@dominio.com',
                password='123qwe',
            )
            self.stdout.write(self.style.SUCCESS('Superusuário criado com sucesso.'))
        else:
            self.stdout.write(self.style.WARNING('Já existe um Superusuário.'))
