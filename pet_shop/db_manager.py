import psycopg2
import os


def conectar_a_db():
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT')
        )
        return conn
    except Exception as error:
        print("Erro ao conectar ao PostgreSQL", error)
        return None


def buscar_dados(conn, query):
    try:
        cur = conn.cursor()
        cur.execute(query)
        data = cur.fetchall()
        cur.close()
        return data
    except Exception as error:
        print("Erro ao buscar dados no PostgreSQL", error)
        return None


def fechar_conexao(conn):
    try:
        conn.close()
    except Exception as error:
        print("Erro ao fechar conexão com o PostgreSQL", error)
