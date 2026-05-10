# ============================================================
# backend/utils/db.py
# Database connection helper
# Creates and returns a MySQL connection using .env settings
# ============================================================

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    """
    Returns a new MySQL database connection.
    Call this at the start of each route function.
    Always close the connection when done!
    """
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "postureguard")
    )
    return connection
