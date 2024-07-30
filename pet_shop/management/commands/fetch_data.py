from django.core.management.base import BaseCommand
from pet_shop.db_manager import conectar_a_db, buscar_dados, fechar_conexao


class Command(BaseCommand):
    help = 'Busca dados do banco de dados PostgresSQL'

    def handle(self, *args, **options):
        conn = conectar_a_db()
        if conn:
            query = "SELECT * FROM usuario"
            dados = buscar_dados(conn, query)
            for row in dados:
                self.stdout.write(str(row))
            fechar_conexao(conn)
