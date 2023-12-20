'''
Author: 		    Mohit Francis
Date:       		27 March 2023
Purpose:    		GISY 6020 - Assignment 4 - Oracle to ArcGIS Pro / Online

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Main Folder:     		MF_MuseumComparison_DataLoad

Main File(s):    		BL_POINT_10K.csv		                          (Attribute table of BL Point 10K layer from BASE_Buildings_GDB_UT83v6_CGVD2013.gdb.)
                    NSTDB_FEATURECODES.xls                        (Data dictionary for BL Point 10K layer, downloaded from NSTDB website.)
                    NSTDB_FEATURECODES.csv                        (Data dictionary converted to CSV format.)
                    vw_hist_buildings.csv                         (The query table / view of Historical Museums exported from Oracle.)
                    vw_exist_buildings.csv                        (The query table / view of Existing Museums exported from Oracle.)
                    config.ini                                    (Contained the now removed login, password, and database name - information required to initialise ETL.)
                    database.py                                   (Creates a connection to Oracle database using credentials contained in config.ini.)
                    insert_BL_POINT_10K.py                        (Inserts data from BL_POINT_10K.csv into specified table in Oracle database.)            
                    insert_NSTDB_FEATURECODES.py                  (Inserts data from NSTDB_FEATURECODES.csv into specified table in Oracle database.)
                    MF_MuseumComparison.sql                       (Complete SQL script which creates tables to store imported CSV data, assigns designations, and creates and exports views.)
                    README.txt							                      (This file: describes files and folders in the MF_MuseumComparison_DataLoad folder.)

Not included due to size: BASE_Buildings_GDB_UT83v6_CGVD2013.gdb  (The original file geodatabase downloaded from the NSTDB website (https://nsgi.novascotia.ca/gdd/) containing the BL Point 10K point layer.)

'''

