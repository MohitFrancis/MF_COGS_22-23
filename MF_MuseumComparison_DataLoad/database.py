'''
Program:    database.py
Programmer: Mohit Francis
Date:       27 March 2023
Purpose:    GISY 6020 - Assignment 4 - Data Loading Module.
            Creates a connection to an Oracle database using the schema present in config.ini.
'''

## Import necessary libraries.
import configparser
import oracledb
from oracledb.connection import Connection

## Get connection to the database.
## The connection parameters will be read from config.ini
def get_connection() -> Connection:

    ## Read the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    ## Initialize the client
    oracledb.init_oracle_client()

    ## Make the connection
    conn = oracledb.connect(
        user=config['credentials']['username'],
        password=config['credentials']['password'],
        dsn=config['connection']['dsn']
    )

    ## Return the connection
    return conn


if __name__ == '__main__':
    ## Read the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    print(config['credentials']['username'])
