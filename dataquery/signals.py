from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_VMpDEhwj40aU@ep-frosty-mouse-a1r1wmnz-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

@receiver(user_logged_out)
def drop_db_on_logout(sender, request, user, **kwargs):
    """Drops the database when the last user logs out."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS data;")
        cursor.close()
        conn.close()
        print("Database dropped after user logout!")
    except Exception as e:
        print(f"Error dropping database: {e}")
