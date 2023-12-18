'''
Program:    MFW0476572_assignment3.py
Programmer: Mohit Francis
Date:       19 April 2023
Purpose:    GISY 6021 - Assignment 3 - Data Loading Module for canadian-airports.csv.
            Connects to the specified schema (see config.ini) in Oracle Cloud Database;
            Creates a reader to access canadian-airports.csv;
            Uses SQL to insert values from CSV file into table created in Oracle schema.
'''


## Import necessary libraries.
import csv 

## Import necessary modules.
import sdo 
import database

## Connect to Oracle Cloud database and create a cursor.
conn = database.get_connection()
cursor = conn.cursor()

## First delete existing values (if any) from associated table in database.
## Commit changes.
cursor.execute('delete from airport')
conn.commit()

## Create a CSV reader object which accesses each row of the CSV file.
with open('canadian-airports.csv', 'r', encoding='utf-8') as g:
    
    reader = csv.reader(g)

    ## Skip the first line in the CSV file.
    next(g)

    ## Parameterised SQL Query for inserting data from canadian-airports.csv into airport table.
    sql = """
        insert into airport 
        values (
            :iata,
            :icao,
            :name,
            :city,
            :location
        )
    """

    ## Iterate over the lines in the reader.
    for r in reader:

        ## Create SDO Point Geometry by fetching, combining, and converting the
        ## longitude and latitude values stored in rows 0 and 1 in the CSV reader.
        ## Assign these combined long/lat values an SDO Geometry Type of 2001 (Point)
        ## and a Coordinate Reference System (CRS) of 4269 (NAD83).
        point = sdo.SDOPointType(float(r[1]), float(r[0]))
        geometry = sdo.SDOGeometry(2001, 4269, point)
        
        ## Access the following columns from the CSV file and insert into named columns in database.
        cursor.execute(sql, {
            'iata': r[2],
            'icao': r[3],
            'name': r[4],
            'city': r[5],
            'location': geometry(conn)
        })

    ## Commit the transaction.
    conn.commit()