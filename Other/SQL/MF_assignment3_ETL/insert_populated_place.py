import csv 

import sdo 
import database


conn = database.get_connection()
cursor = conn.cursor()

cursor.execute('delete from populated_place')
conn.commit()

with open('canadian-geographical-names.csv', 'r', encoding='utf-8') as g:
    reader = csv.reader(g)
    next(g)
    sql = """
        insert into populated_place 
        values (
            :cgndb_id,
            :geo_name,
            :code,
            :centroid
        )
    """
    for r in reader:
        point = sdo.SDOPointType(float(r[4]), float(r[3]))
        geometry = sdo.SDOGeometry(2001, 4269, point)
        cursor.execute(sql, {
            'cgndb_id': r[0],
            'geo_name': r[1],
            'code': r[2],
            'centroid': geometry(conn)
        })
    conn.commit()