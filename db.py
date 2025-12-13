import psycopg2

def get_db():
    return psycopg2.connect(
        host="dpg-d4tijl63jp1c73d3bvj0-a.oregon-postgres.render.com",
        port=5432,
        user="planetter2_db_user",
        password="3VfanMp4yvHo7xMJdKklRayJOmLvV6ME",
        dbname="planetter2_db",
        sslmode="require"
    )