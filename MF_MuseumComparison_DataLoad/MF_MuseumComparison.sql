/*
  Program:    MFW0476572_GISY6020_Assn4.sql
  Programmer: Mohit Francis - W0476572
  Class:      GISY 6020 - Advanced GIS
  Date:       27 March 2023
  Purpose:    Data Loading and View Creation in Oracle Cloud.
*/

-- ***********************
-- Gain VIEW creation privileges on current SCHEMA.
-- ***********************

---- use ADMIN user to grant ADVGIS_A4 permission to create Views.
-- GRANT CREATE VIEW TO ADVGIS_A4;


-- **********************
-- Creating Tables and Constraints for data to be imported.
-- **********************

-- Table to store data from BL_POINT_10K.csv import (building points data).
-- Create PRIMARY KEY constraint on OBJECTID.
CREATE TABLE   BL_POINT_10K
    (
    OBJECTID NUMBER(8),
    FEAT_CODE VARCHAR2(10),
    FEAT_DESC VARCHAR2(250),
    OBJECTID NUMBER(8),
	ZVALUE NUMBER(8,3),
    CONSTRAINT BL_POINT_10K_OBJECTID_pk PRIMARY KEY (OBJECTID)
    );
	
-- Table to store data from NSTDB_FEATURECODES.csv import (building code data dictionary).
-- Create PRIMARY KEY constraint on FEAT_CODE.
CREATE TABLE   NSTDB_FEATURECODES
    (
    FEAT_CODE VARCHAR2(10),
    DESCRIPTION VARCHAR2(250),
    LAYER VARCHAR2(100),
    PRODUCT VARCHAR2(20),
    CONSTRAINT NSTDB_FEATURECODES_FEAT_CODE_pk PRIMARY KEY (FEAT_CODE)
    );


-- ***********************
-- Data Loading.
-- ***********************

-- Check error tables for data loading errors. None observed.
SELECT * FROM SDW$ERR$_BL_POINT_10K;
SELECT * FROM SDW$ERR$_NSTDB_FEATURECODES;

-- Drop error tables.
DROP TABLE SDW$ERR$_BL_POINT_10K;
DROP TABLE SDW$ERR$_NSTDB_FEATURECODES;

-- This is the main data table.
-- Check to see if all records were imported into Oracle.
SELECT COUNT(*) FROM BL_POINT_10K;
-- 553,240 records - yes, all were imported.

-- This is the lookup Table.
SELECT COUNT(*) FROM NSTDB_FEATURECODES;
-- 698 records - yes, all were imported.


-- ***********************
-- Creating Status Table.
-- ***********************

-- Create a temporary table to store all 553240 buildings in NSTDB_BL_POINT_10K.
CREATE TABLE building_status_temp(
    shape_FID NUMBER(8),
    status VARCHAR2(10)
);

-- Create a temporary table to store status information for the above buildings.
CREATE TABLE random_status_values(
    p_id NUMBER GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),
    status_random VARCHAR2(10)
);

-- Insert distinct buildings (via their shape_FIDs) into the temporary building table.
-- from BL_POINT_10K.
INSERT INTO building_status_temp(shape_FID)
    SELECT DISTINCT(SHAPE_FID) FROM BL_POINT_10K;

-- Randomly generate either 'Existing' or 'Historical' statuses for all 553,240 buildings, and insert into
-- random_status_values table.
INSERT INTO random_status_values (status_random)
    SELECT DECODE(ROUND(DBMS_RANDOM.VALUE), 1, 'Existing', 'Historical') rnd FROM dual
    CONNECT BY LEVEL <= 553240;

-- Check to see if inserts are successful.
SELECT * FROM building_status_temp;
-- Shape_FID column is filled, Status column is currently all NULLs.

SELECT * FROM random_status_values;
-- P_ID column is auto-increment, Status column is currently filled with randomly generated statuses.

-- Check to see if the number of rows in both tables are the same.
SELECT COUNT(*) FROM building_status_temp;
-- Yes, 553,240.

SELECT COUNT(*) FROM random_status_values;
-- Yes, 553,240.

-- Create the actual table for all buildings in NSTDB_BL_POINT_10K.
-- This stores shape_FID and randomly assigns either Historical or Existing status to each building.
CREATE TABLE building_status(
    shape_FID number(8),
    status varchar2(10),
    CONSTRAINT building_status_shape_FID_pk PRIMARY KEY(shape_FID)
);

-- Use CTEs to join the temporary tables. Since the two temporary tables do not have
-- common fields, use ROWNUM as the join field. This will assign the 553,240 buildings
-- with their own status, either Historical or Existing.
-- Insert results of the join into the actual BUILDING_STATUS table.
INSERT INTO building_status (shape_FID, status)
    WITH randomBuildings AS(
                            SELECT ROWNUM id, shape_FID, status FROM
                                    (SELECT * FROM building_status_temp)),
    randomValues AS(
                            SELECT ROWNUM id, p_id, status_random FROM
                                    (SELECT * FROM random_status_values
                                    ORDER BY DBMS_RANDOM.VALUE))
    SELECT shape_FID, status_random
    FROM randomBuildings
    JOIN randomValues USING(id);

-- Check to see if join and insert worked, i.e. correct number of rows,
-- no NULLS, all buildings have an assigned status.
SELECT COUNT(*) FROM building_status;
-- yes, 553,240 rows.

SELECT * FROM building_status
WHERE status IS NULL;
-- no rows where status is NULL.

SELECT * FROM building_status
WHERE shape_FID IS NULL;
-- no rows where shape_FID is NULL.

-- Drop temporary tables since random generation and status assignment was successful.
DROP TABLE building_status_temp;
DROP TABLE random_status_values;


-- ***********************
-- Creating Views for Historical and Existing Buildings
-- ***********************

-- ALTER table to add a new column with specified format
-- so ArcGIS Pro can import and read the table with no issues.
ALTER TABLE BL_POINT_10K
ADD (PKey NUMBER(8,0));

-- UPDATE the new PKey column and set it to values in objectid column.
UPDATE BL_POINT_10K
SET PKey = objectid;

-- ALTER table to add a primary key constraint and set it to PKey column.
ALTER TABLE BL_POINT_10K
ADD CONSTRAINT BL_POINT_10K_objectid_pk PRIMARY KEY(PKey);

-- View columns in BL_POINT_10K table for join fields.
SELECT * FROM BL_POINT_10K;

-- View columns in NSTDB_FEATURECODES table for join fields.
SELECT * FROM NSTDB_FEATURECODES;

-- View columns in BUILDING_STATUS table for join fields.
SELECT * FROM BUILDING_STATUS;

-- Find and count feat_codes of interest. Counts of feat_codes between 20-50
-- when split between historical and existing buildings are of greatest interest.
SELECT feat_code, count(feat_code) FROM BL_POINT_10K
GROUP BY feat_code;

-- BLMU60 are Museums. There are 97 Museums in total in the data set.
SELECT * FROM NSTDB_FEATURECODES WHERE feat_code = 'BLMU60';

-- Create view showing random selection of ~50 Historical buildings, by joining the above three tables.
CREATE OR REPLACE VIEW vw_hist_buildings AS
    SELECT
        a.PKey,
        a.zvalue Height,
        a.feat_code FCode,
        b.description Description,
        c.status Status
    FROM
        BL_POINT_10K a,
        NSTDB_FEATURECODES b,
        BUILDING_STATUS c
    WHERE
        a.feat_code = b.feat_code(+) AND
        a.shape_FID = c.shape_FID(+) AND
        c.status = 'Historical' AND
        a.feat_code = 'BLMU60';

-- Create view showing random selection of ~50 Existing buildings, by joining the above three tables.
CREATE OR REPLACE VIEW vw_exist_buildings AS
    SELECT
        a.PKey,
        a.zvalue Height,
        a.feat_code FCode,
        b.description Description,
        c.status Status
    FROM
        BL_POINT_10K a,
        NSTDB_FEATURECODES b,
        BUILDING_STATUS c
    WHERE
        a.feat_code = b.feat_code(+) AND
        a.shape_FID = c.shape_FID(+) AND
        c.status = 'Existing' AND
        a.feat_code = 'BLMU60';

-- View the Historical Building view.
SELECT * FROM vw_hist_buildings;

-- View the Existing Building view.
SELECT * FROM vw_exist_buildings;