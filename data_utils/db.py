import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from pydantic import BaseModel, Field

# Database connection parameters from environment variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Connection pool
pool = None


# Initialize the connection pool
def initialize_pool():
    global pool
    if pool is None:
        pool = SimpleConnectionPool(
            1,
            20,  # min and max connections
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME,
        )
    return pool


# Connection manager to safely get and release connections
@contextmanager
def get_connection():
    if pool is None:
        initialize_pool()

    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)
