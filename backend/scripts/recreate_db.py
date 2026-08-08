"""One-off dev utility: drops and recreates the zivastockdb database.
Run manually: python scripts/recreate_db.py
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_NAME = "zivastockdb"
CONN_PARAMS = dict(host="localhost", port=5432, dbname="postgres", user="postgres", password="Laugh@2012")


def main():
    conn = psycopg2.connect(**CONN_PARAMS)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    print(f"Terminating active connections to {DB_NAME}...")
    cur.execute(
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s AND pid <> pg_backend_pid();",
        (DB_NAME,),
    )

    print(f"Dropping database {DB_NAME} if exists...")
    cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(DB_NAME)))

    print(f"Creating database {DB_NAME}...")
    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))

    cur.close()
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
