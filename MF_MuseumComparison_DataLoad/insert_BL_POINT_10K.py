'''
Program:    insert_BL_POINT_10K.py
Programmer: Mohit Francis
Date:       27 March 2023
Purpose:    GISY 6020 - Assignment 4 - Data Loading Module for BL_POINT_10K.csv.
            Connects to the specified schema (see config.ini) in Oracle Cloud Database;
            Creates a reader to access BL_POINT_10K.csv.;
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
cursor.execute('delete from BL_POINT_10K')
conn.commit()

## Create a CSV reader object which accesses each row of the CSV file.
with open('BL_POINT_10K.csv', 'r', encoding='utf-8') as g:
    
    reader = csv.reader(g)
    
    ## Skip the first line in the CSV file.
    next(g)
    
    ## Parameterised SQL Query for inserting data from BL_POINT_10K.csv into the BL_POINTS_10K table.
    sql = """
        insert into BL_POINT_10K 
        values (
            :OBJECTID,
            :FEAT_CODE,
            :FEAT_DESC,
            :ZVALUE,
            :SHAPE_FID
        )
    """

    ## Iterate over the lines in the reader.
    for r in reader:

        ## Access the following columns from the CSV file and insert into named columns in database.
        cursor.execute(sql, {
            'OBJECTID': r[0],
            'FEAT_CODE': r[1],
            'FEAT_DESC': r[2],
            'ZVALUE': r[3],
            'SHAPE_FID': r[4]
        })

    ## Commit the transaction.
    conn.commit()