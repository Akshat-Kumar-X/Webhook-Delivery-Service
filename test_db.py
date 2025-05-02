import psycopg2, redis

pg = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="admin",  # use the actual password from your docker-compose.yml
    dbname="postgres"
)
cur = pg.cursor()
cur.execute("SELECT version()")
print("Postgres version:", cur.fetchone())

r = redis.from_url("redis://localhost:6379/0")
r.set("milestone1", "✅")
print("Redis says:", r.get("milestone1"))
