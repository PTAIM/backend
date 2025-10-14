import sys
from sqlalchemy import text

from app.core import database


def main():
    print("Usando DATABASE_URL:", database.DATABASE_URL)
    try:
        with database.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("Conexão OK: SELECT 1 retornou 1")
                return 0
            else:
                print("Conexão estabelecida, mas SELECT 1 não retornou 1")
                return 2
    except Exception as e:
        print("Falha ao conectar no banco:")
        print(repr(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())