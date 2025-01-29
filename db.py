import logging
from mysql.connector import pooling, Error

# Configure logging to write logs to a file
logging.basicConfig(
    filename="app.log",  # Log file name
    level=logging.INFO,  # Log level: INFO, DEBUG, WARNING, ERROR
    format="%(asctime)s [%(levelname)s] %(message)s"  # Log format with timestamp
)

# Set up a MySQL connection pool
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="mypool",               # Name of the pool
        pool_size=5,                      # Maximum number of active connections in the pool
        pool_reset_session=True,          # Resets session state when connection is returned
        host="voyager-db-2.csxamwsgs3o0.us-east-1.rds.amazonaws.com",
        user="admin",
        password="12345678",
        database="Voyager"        # Replace with your database name
    )
    logging.info("MySQL connection pool created successfully.")
except Error as e:
    logging.critical(f"Error creating MySQL connection pool: {e}")
    raise

def get_db_connection():
    """
    Get a connection from the connection pool.

    Returns:
        MySQLConnection: A connection object from the pool.

    Raises:
        Error: If unable to get a connection from the pool.
    """
    try:
        connection = connection_pool.get_connection()
        logging.info("Database connection acquired from the pool.")
        return connection
    except Error as e:
        logging.error(f"Error getting database connection: {e}")
        raise

def close_connection(connection):
    """
    Safely close the connection and return it to the pool.

    Args:
        connection (MySQLConnection): The connection object to be closed.
    """
    try:
        if connection.is_connected():
            connection.close()
            logging.info("Database connection returned to the pool.")
    except Error as e:
        logging.warning(f"Error closing the database connection: {e}")
