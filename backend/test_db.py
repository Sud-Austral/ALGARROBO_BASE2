import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
print(f"Testing URL: {url.split('@')[1] if '@' in url else 'Invalid URL'}")

try:
    conn = psycopg2.connect(url, connect_timeout=10)
    print("Conexión exitosa!")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
