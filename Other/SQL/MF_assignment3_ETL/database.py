"""Create a connection to an Oracle database"""

import configparser
import oracledb
from oracledb.connection import Connection


def get_connection() -> Connection:
    """Get a connection to the database
    
       The connection parameters will be read from config.ini
    """
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Initialize the client
    oracledb.init_oracle_client()

    # Make the connection
    conn = oracledb.connect(
        user=config['credentials']['username'],
        password=config['credentials']['password'],
        dsn=config['connection']['dsn']
    )

    # Return the connection
    return conn


if __name__ == '__main__':
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    print(config['credentials']['username'])