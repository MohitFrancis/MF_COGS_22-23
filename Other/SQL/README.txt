'''
Author: 		Mohit Francis
Date:       		Various, see headers
Purpose:    		Various - assignment submissions for GISY 6021 - Information Systems

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Main Folder:     		Other / SQL

Main File(s):    		README.txt							(This file: describes files and folders in the Other / SQL directory.)

Subfolder(s):			MF_assignment2_PLSQL						
				MF-assignment3_ETL						
			
Subfile(s):			MF_assignment2 / MF_assignment2.sql				(Oracle PL/SQL script for converting values between various units of measure.)

				MF-assignment3_ETL / canadian-airports.csv			(Tidied Canadian airport location data provided for assignment.)
				MF-assignment3_ETL / canadian-geographical-names.csv		(Tidied Canadian place names data provided for assignment.)
				MF-assignment3_ETL / canadian-province-simplify.csv		(Simplified Canadian province polgyon data provided for assignment.)
				MF-assignment3_ETL / config.ini					(Contained the now removed login, password, and database name - information required to initialise ETL.)
				MF-assignment3_ETL / database.py				(Creates a connection to Oracle database using credentials contained in config.ini.)
				MF-assignment3_ETL / sdo.py					(Initialises and sets the necessary types of SDO spatial objects within Oracle database.)
				MF-assignment3_ETL / insert_airport.py				(Inserts data from canadian-airports.csv into Oracle database.)
				MF-assignment3_ETL / insert_populated_place.py			(Inserts data from canadian-geographical-names.csv into Oracle database.)
				MF-assignment3_ETL / insert_province_pool			(Inserts data from canadian-province-simplify.csv into Oracle database.)
				MF-assignment3_ETL / OracleSpatialQueries.sql			(SQL script for creating tables containing geometry, inserting geometry metadata, creating spatial indices on spatial tables, and executing spatial queries.)
				MF-assignment3_ETL / MFW0476572_assignment-3.docx		(Word document containing Oracle Spatial query results.)
				MF-assignment3_ETL / MFW0476572_assignment-3.pdf		(PDF document containing Oracle Spatial query results, derived from MFW0476572_assignment-3.docx.)


'''
