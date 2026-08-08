import sys
try:
    import psycopg2
except ImportError:
    print("psycopg2 not installed")
    sys.exit(1)

try:
    conn = psycopg2.connect(host="localhost", port=5432, dbname="zivastockdb", user="postgres", password="Laugh@2012", connect_timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name;")
    print("TABLES:", [r[0] for r in cur.fetchall()])
    cur.execute("SELECT table_name FROM information_schema.views WHERE table_schema='public' ORDER BY table_name;")
    print("VIEWS:", [r[0] for r in cur.fetchall()])
    cur.execute("SELECT routine_name FROM information_schema.routines WHERE routine_schema='public' ORDER BY routine_name;")
    print("FUNCTIONS:", [r[0] for r in cur.fetchall()])
    cur.execute("SELECT name, is_system FROM roles ORDER BY id;")
    print("ROLES:", cur.fetchall())
    cur.execute("SELECT count(*) FROM permissions;")
    print("PERMISSIONS COUNT:", cur.fetchone()[0])
    conn.close()
except Exception as e:
    print("CONNECT FAILED:", repr(e))

try:
    import redis
    r = redis.Redis(host="localhost", port=6379, socket_connect_timeout=3)
    print("REDIS PING:", r.ping())
except Exception as e:
    print("REDIS FAILED:", repr(e))
