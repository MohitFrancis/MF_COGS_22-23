'''
Program:    insert_NSTDB_FEATURECODES.py
Programmer: Mohit Francis
Date:       27 March 2023
Purpose:    GISY 6020 - Assignment 4 - Data Loading Module for NSTDB_FEATURECODES.csv.
            Connects to the specified schema (see config.ini) in Oracle Cloud Database;
            Creates a reader to access NSTDB_FEATURECODES.csv;
            Uses SQL to insert values from CSV file into table created in Oracle schema.
'''



## Import necessary libraries.
import csv 

## Import necessary modules.
import database

## Connect to Oracle Cloud database and create a cursor.
conn = database.get_connection()
cursor = conn.cursor()

## First delete existing values (if any) from associated table in database.
## Commit changes.
cursor.execute('delete from NSTDB_FEATURECODES')
conn.commit()

## Create a CSV reader object which accesses each row of the CSV file.
with open('NSTDB_FEATURECODES.csv', 'r', encoding='utf-8') as g:
    

    reader = csv.reader(g)
    
    ## Skip the first line in the CSV file.
    next(g)

    ## Parameterised SQL Query for inserting data from NSTDB_FEATURECODES.csv into the NSTDB_FEATURECODES table.
    sql = """
        insert into NSTDB_FEATURECODES 
        values (
            :FEAT_CODE,
            :DESCRIPTION,
            :LAYER,
            :PRODUCT
        )
    """

    ## Iterate over the lines in the reader.
    for r in reader:

        ## Access the following columns from the CSV file and insert into named columns in database.
        cursor.execute(sql, {
            'FEAT_CODE': r[0],
            'DESCRIPTION': r[1],
            'LAYER': r[2],
            'PRODUCT': r[4]
        })

    ## Commit the transaction.
    conn.commit()