import csv
import json
import os
from multiprocessing import Pool

import sdo 
import database


conn = database.get_connection()
cursor = conn.cursor()


def task(name, geometry):
    # Create an instance of the Oracle JSON reader class
    sdo_geometry_reader = sdo.OracleJSONGeometryReader()
    sdo_geometry = sdo_geometry_reader.to_sdo_geometry(json.loads(geometry))
    # Insert 
    cursor.execute("""
        insert into province (name, border)
        values (
            :name,
            :border
        )
    """, {
        'name': name, 
        'border': sdo_geometry(conn)
    })
    # Commit the transaction
    conn.commit()


def print_error(e):
    print(e)


if __name__ == '__main__':
    # Configure the field size limit for importing
    # long strings.
    csv.field_size_limit(2147483647)

    # Delete from the province table
    cursor.execute('delete from province')
    conn.commit()

    # Get a pool of workers - x the number of CPUs
    pool = Pool(os.cpu_count())

    with open('canadian-province-simplify.csv', 'r', encoding='utf-8') as g:
        # Move to the next line to skip the header
        next(g)
        # Reader 
        reader = csv.reader(g)
        # For each row 
        for r in reader:
            # Use apply_async 
            pool.apply_async(task, args=(r[0], r[1]), error_callback=print_error)
        # Close the pool
        pool.close()
        pool.join()
    # Commit the transaction 
    conn.commit()
