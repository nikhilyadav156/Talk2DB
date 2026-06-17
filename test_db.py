from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = quote_plus(os.getenv('DB_PASSWORD', 'nikhilroot7'))
DB_NAME = os.getenv('DB_NAME', 'talk2db')

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f"URL: {DB_URL}")

engine = create_engine(DB_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES"))
        print("Connected! Tables found:")
        for row in result:
            print(" -", row[0])
except Exception as e:
    print("Connection failed:", e)