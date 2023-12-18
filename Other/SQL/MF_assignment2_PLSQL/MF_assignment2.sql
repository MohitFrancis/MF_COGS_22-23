/*
  Program:    MFW0476572_assignment-2.sql
  Programmer: Mohit Francis - W0476572
  Class:      GISY 6021
  Date:       22 March 2023
  Purpose:    Creating PL/SQL functions, procedures, and handling exceptions; Loading and mapping
              denormalised data file into Oracle Cloud Database, then normalising, querying and analysing data
              using stored functions.
*/


-- *********************************
-- Creating Error Table for Exception Handling and Debugging.
-- *********************************

-- Create a table to store error messages which can be used for debugging.
CREATE TABLE error_log(
    error_date      TIMESTAMP(6),
    subprogram_name VARCHAR2(128),
    error_code      INTEGER,
	error_message   VARCHAR2(512),
	error_backtrace CLOB,
    error_callstack CLOB,
	created_by      VARCHAR2(30)
);

-- Create a procedure for inserting the error data.
CREATE OR REPLACE PROCEDURE insert_error_log AS 

    -- Autonomous transaction means that the insert should be committed even
    -- if there is a rollback as a result of the error that caused this.
    PRAGMA AUTONOMOUS_TRANSACTION;

    -- Get the name of the subprogram that called this insert.
    subprogram_name VARCHAR2(128) := utl_call_stack.concatenate_subprogram(utl_call_stack.subprogram(2));
	
	-- Error code.
	error_code INTEGER := SQLCODE;
	
	-- Error message.
	error_message VARCHAR2(512) := SQLERRM;

BEGIN

    -- Insert values into the error log table.    
    INSERT INTO error_log
    VALUES (
        SYSDATE,
        subprogram_name,
        error_code,
        error_message,
        DBMS_UTILITY.FORMAT_ERROR_BACKTRACE,
        DBMS_UTILITY.FORMAT_CALL_STACK,
        USER
    );

    -- Since this is an autonomous transaction it must be committed.
    COMMIT;

END;


-- *********************************
-- Creating a Custom PL/SQL Function for Converting Between Units.
-- *********************************

-- Look at column names of sdo_units_of_measure table.
DESC sdo_units_of_measure;

/*
Name               Null?    Type           
------------------ -------- -------------- 
UOM_ID             NOT NULL NUMBER(10)     
UNIT_OF_MEAS_NAME  NOT NULL VARCHAR2(2083) 
SHORT_NAME                  VARCHAR2(80)   
LEGACY_UNIT_NAME            VARCHAR2(80)   
UNIT_OF_MEAS_TYPE           VARCHAR2(50)   
TARGET_UOM_ID               NUMBER(10)     
FACTOR_B                    NUMBER         
FACTOR_C                    NUMBER         
INFORMATION_SOURCE          VARCHAR2(254)  
DATA_SOURCE                 VARCHAR2(40)   
IS_LEGACY          NOT NULL VARCHAR2(5)    
LEGACY_CODE                 NUMBER(10)
*/

-- Look at records in sdo_units_of_measure_table.
SELECT
    *
FROM
    sdo_units_of_measure;

-- Create procedure which will access the sdo units of measure table and find
-- the record which matches the user's input.
CREATE OR REPLACE PROCEDURE unit_table_query(
                                            unit_name_input IN VARCHAR2,
                                            unit_type OUT VARCHAR2,
                                            factor1 OUT NUMBER,
                                            factor2 OUT NUMBER) IS

-- Declare user defined error here. May
-- the record which matches the user's input.
    invalid_unit EXCEPTION;
    PRAGMA EXCEPTION_INIT(invalid_unit, -20000);

BEGIN

    SELECT
        unit_of_meas_type,
        factor_b,
        factor_c
    INTO
        unit_type,
        factor1,
        factor2
    FROM
        sdo_units_of_measure
    WHERE
        UPPER(unit_name_input) = UPPER(short_name);

EXCEPTION

    WHEN NO_DATA_FOUND THEN
        RAISE invalid_unit;
        insert_error_log;
        
END;


-- Create function which asks for user to input a value, and the units to convert from
-- and the units to convert to. This function will access the sdo units of measure table,
-- pull records which match the user's input, and perform the conversion calculation
-- using a conversion factor to produce the output value.

-- *** Note: The Function half-works. Converting between like units works fine.
-- *** However, the user defined errors are not raised, though inputting invalid units
-- *** or using units of different types returns NULL values or other errors instead, respectively.
-- *** Unfortunately, I could not diagnose the issue and I ran out of time when debugging :(
CREATE OR REPLACE FUNCTION COGS_CONVERT_UNIT(
    from_val NUMBER,                    -- The three inputs of the function.
    from_convert_unit_input VARCHAR2,
    to_convert_unit_input VARCHAR2)
    RETURN NUMBER IS

    -- Two user-defined exceptions are declared - one for units not found in the
    -- sdo units of measure table, and the other for converting between units of different
    -- types. Unfortunately, these user defined errors are not raised.
    invalid_unit EXCEPTION;
    PRAGMA EXCEPTION_INIT(invalid_unit, -20000);

    diff_unit_types EXCEPTION;
    PRAGMA EXCEPTION_INIT(diff_unit_types, -20999);

    -- Variables which will store the results of the procedure, called twice for the to and from units.
    from_short_name VARCHAR2(80);
    from_unit_type VARCHAR2(50);
    from_factor_b NUMBER;
    from_factor_c NUMBER;

    to_short_name VARCHAR2(80);
    to_unit_type VARCHAR2(50);
    to_factor_b NUMBER;
    to_factor_c NUMBER;

    -- The calculation and final output variables.
    conversion_factor NUMBER;
    to_val NUMBER;

BEGIN

    -- The function only seems to work when nested, not sure why.
    BEGIN
    
        unit_table_query(from_convert_unit_input, from_unit_type, from_factor_b, from_factor_c);
        unit_table_query(to_convert_unit_input, to_unit_type, to_factor_b, to_factor_c);

    -- If the user input units are not found in the sdo units of measure table, then raise error. Does not work.
        IF from_short_name IS NULL OR to_short_name IS NULL THEN
            RAISE invalid_unit;
        END IF;

    EXCEPTION    

    -- Insert various error information into error log table, defined above. The error messages also do not display.
        WHEN invalid_unit THEN
            DBMS_OUTPUT.PUT_LINE('Error ' || SQLCODE || ': Unknown or unsupported Unit Name(s) and/or incorrect format for Unit Name(s) in Oracle Cloud 19C. Use "SELECT DISTINCT short_name FROM sdo_units_of_measure" query for list of supported units and correct input format.');
            insert_error_log;

    END;

    -- If the unit types do not match, then raise error. Does not work.     
    IF from_unit_type != to_unit_type THEN
        RAISE diff_unit_types;
    END IF;

    -- If the from unit is the same as the to unit, return the input value. Not sure if this works as coded
    -- but no issues were found in the output.    
    IF to_short_name = from_short_name THEN
        DBMS_OUTPUT.PUT_LINE('The units are the same. The value is ' || from_val);
        RETURN from_val;
    END IF;

    -- The conversion factor uses the values assigned to variables which were called in the procedure.
    -- Multiply the input value by the conversion factor to output the final result.
    conversion_factor := (from_factor_b / to_factor_c) * (from_factor_c / to_factor_b);
    to_val := from_val * conversion_factor;
    RETURN to_val;
    
EXCEPTION
    
    -- Insert various error information into error log table, defined above. The error messages also do not display.
    WHEN diff_unit_types THEN
        DBMS_OUTPUT.PUT_LINE('Error ' || SQLCODE || ': Unit Types (Angle, Area, Length, Scale, Volume) of Input Units are not the same. Units of different types cannot be converted. Please try again!');
        insert_error_log;

    
    WHEN no_data_found THEN
        DBMS_OUTPUT.PUT_LINE('Error ' || SQLCODE || ': Unknown or unsupported Unit Name(s) and/or incorrect format for Unit Name(s) in Oracle Cloud 19C. Use "SELECT DISTINCT short_name FROM sdo_units_of_measure" query for list of supported units and correct input format.');
        insert_error_log;

END;


-- *********************************
-- Testing the Function and Producing Error Log.
-- *********************************

-- This select statement should return 0.001.
SELECT
    cogs_convert_unit(1, 'metre', 'kilometre')
FROM
    dual;
-- Yes, it does.    

-- This select statement should return 0.001.
SELECT
    cogs_convert_unit(1, 'Metre', 'KILOMETRE')
FROM
    dual;
-- Yes, it does.

-- This select statement should return 0.001.
SELECT
    cogs_convert_unit(1, 'mEtRe', 'KiLoMeTrE')
FROM
    dual;
-- Yes, it does.

-- This select statement should raise the error related to
-- converting between units of different types.
SELECT
    cogs_convert_unit(1, 'radian', 'kilometre')
FROM
    dual;
-- No, it does not raise user defined error, but it does raise a different error.

-- This select statement should raise the unsupported
-- unit error.
SELECT
    cogs_convert_unit(1, 'football_pitch', 'acres')
FROM
    dual;
-- No, it does not raise user defined error, but it does return a NULL value.

-- Call all records in the error log table.
SELECT
    *
FROM
    error_log;

-- Call all the two most recent records in the error log table, caused by the
-- the last two test cases.
SELECT
    *
FROM
    error_log
FETCH NEXT 2 ROWS ONLY;


-- *********************************
-- Data Loading.
-- *********************************

-- province-federal-electoral-district.csv loaded into Oracle Cloud Database as table electoral_district.
-- The DESCRIBE statement displays which parameters were used when loading the table.
DESCRIBE electoral_district;

/*
Name     Null? Type          
-------- ----- ------------- 
PRUID          NUMBER(2)     
PRNAME         VARCHAR2(150) 
PRENAME        VARCHAR2(75)  
PRFNAME        VARCHAR2(75)  
PREABBR        VARCHAR2(15)  
PRFABBR        VARCHAR2(15)  
FEDUID         NUMBER(5)     
FEDDGUID       VARCHAR2(14)  
FEDNAME        VARCHAR2(75)  
LANDAREA       NUMBER        
GEOJSON        CLOB     
*/

-- Check error table for errors, none were reported.
SELECT * FROM
SDW$ERR$_ELECTORAL_DISTRICT;

-- Drop error table after errors checked and none were reported.
DROP TABLE
SDW$ERR$_ELECTORAL_DISTRICT;


-- *********************************
-- Normalisation.
-- *********************************

-- Use this query to look at sample record of table.
SELECT * FROM electoral_district
FETCH NEXT 1 ROW ONLY;

-- COUNT total number of rows in the newly loaded table.
SELECT COUNT(*) FROM ELECTORAL_DISTRICT;

-- COUNT number of DISTINCT values in each column.
-- Leave out GEOJSON column from COUNT because it is an object
-- and not a value that can be counted.
SELECT
    COUNT(DISTINCT pruid),
    COUNT(DISTINCT prname),
    COUNT(DISTINCT prename),
    COUNT(DISTINCT prfname),
    COUNT(DISTINCT preabbr),
    COUNT(DISTINCT prfabbr),
    COUNT(DISTINCT feduid),
    COUNT(DISTINCT feddguid),
    COUNT(DISTINCT fedname),
    COUNT(DISTINCT landarea)
FROM
    ELECTORAL_DISTRICT;
-- There are only 4 DISTINCT provinces, but the number of DISTINCT federal electoral districts
-- equals the total number of rows in the data set.


-- Therefore, to normalise this data set, create 3 tables in total:
-- Separate the bilingual province names to create two separate lookup tables;
-- Create one main table for federal electoral district land area.

-- Create lookup table to store province names and abbrevations in English.
-- Add PRIMARY KEY CONSTRAINT on pruid.
CREATE TABLE province_name_eng (
    pruid   NUMBER,
    prename  VARCHAR2(50),
    preabbr  VARCHAR2(6),
    CONSTRAINT province_name_eng_pr_uuid_pk PRIMARY KEY(pruid)
);

-- Insert DISTINCT English province names and abbrevations into lookup table.
INSERT INTO PROVINCE_NAME_ENG
    SELECT DISTINCT pruid, prename, preabbr
    FROM electoral_district;

-- Create lookup table to store province names and abbrevations in French.
-- Add PRIMARY KEY CONSTRAINT on pruid.
CREATE TABLE province_name_fr (
    pruid   NUMBER,
    prfname  VARCHAR2(50),
    prfabbr  VARCHAR2(10),
    CONSTRAINT province_name_fr_pr_uuid_pk PRIMARY KEY(pruid)
);

-- Insert DISTINCT French province names and abbrevations into lookup table.
INSERT INTO province_name_fr
    SELECT DISTINCT pruid, prfname, prfabbr
    FROM electoral_district;

-- Create main table to store federal electoral data. This main table also includes
-- the pruid (province id) column as well.
-- Add PRIMARY KEY CONSTRAINT on feduid; FOREIGN KEY CONSTRAINTS on pruid to relate to lookup tables.
CREATE TABLE federal_elec_district (
    pruid NUMBER,
    feduid NUMBER,
    feddguid VARCHAR2(20),
    district_name VARCHAR2(100),
    landarea NUMBER,
    GEOJSON CLOB,
    CONSTRAINT federal_elec_district_feduid_pk PRIMARY KEY(feduid),
    CONSTRAINT federal_elec_districtTOprovince_name_eng_pruid_fk FOREIGN KEY (pruid) REFERENCES province_name_eng(pruid),
    CONSTRAINT federal_elec_districtTOprovince_name_fr_pruid_fk FOREIGN KEY (pruid) REFERENCES province_name_fr(pruid)
);

-- Insert federal electoral data into main table.
-- No need to use DISTINCT keyword since all feduids in this data set are DISTINCT.
INSERT INTO federal_elec_district
    SELECT pruid, feduid, feddguid, fedname, landarea, geojson
    FROM electoral_district;

-- Add a new column called geometry with type SDO_GEOMETRY.
ALTER TABLE federal_elec_district
ADD geometry sdo_geometry;

-- Update the new column named geometry to a geometry value
-- based on the values in the geojson column.
UPDATE federal_elec_district
SET geometry = SDO_UTIL.FROM_GEOJSON(geojson);

-- Remove geojson column from main table.
ALTER TABLE federal_elec_district
DROP COLUMN geojson;

-- Examine normalised data model.
-- Examine finalised main table.
SELECT
    *
FROM
    federal_elec_district
FETCH NEXT 1 ROWS ONLY;

-- Examine finalised English province name lookup table.
SELECT
    *
FROM
    province_name_eng;

-- Examine finalised French province name lookup table.
SELECT
    *
FROM
    province_name_fr;

-- Recreate original denormalised table using a query.
SELECT
    a.pruid,
    b.prename || ' / ' || c.prfname "prname",
    b.prename,
    b.preabbr,
    c.prfname,
    c.prfabbr,
    a.feduid,province_name_fr,
    a.feddguid,
    a.district_name "fedname",
    a.landarea,
    a.geometry
FROM federal_elec_district a
JOIN province_name_eng b ON a.pruid = b.pruid
JOIN province_name_fr c ON a.pruid = c.pruid;

-- Insert the geometry metadata for the normalised data model.
INSERT INTO user_sdo_geom_metadata
VALUES (
    'federal_elec_district',            -- This is the name of the table containing the SDO_GEOMETRY column.
    'geometry',                         -- This is the name of the SDO_GEOMETRY column.
    SDO_DIM_ARRAY (
        SDO_DIM_ELEMENT('LON', -180, 180, 0.05),
        SDO_DIM_ELEMENT('LAT', -90, 90, 0.05)
    ),
    4326
);

-- *********************************
-- Analysis and Querying Data.
-- *********************************

-- Query 1: What is the difference between this calculated value and the LANDAREA
-- column values as a percentage of the LANDAREA column? Give the name of the federal
-- electoral district, the LANDAREA, the calculated area and the percentage in your answer.
-- Use the SDO_AREA function to calculate areas of the geometries in your database. The CRS
-- of the data is a geographic CRS (EPSG::4326) so the result of this function will be in
-- units of square metres. Use your COGS_CONVERT_UNIT function to convert the result to square kilometres.

SELECT
    district_name "Federal District Name",
    ROUND(landarea, 2) "Recorded Land Area (Square kilometres, Sq. Km)", 
    ROUND(COGS_CONVERT_UNIT(SDO_GEOM.SDO_AREA(geometry, 0.005), 'sq_meter', 'sq_kilometer'), 2) "Calculated Land Area (Square kilometres, Sq. Km)",
    ROUND((COGS_CONVERT_UNIT(SDO_GEOM.SDO_AREA(geometry, 0.005), 'sq_meter', 'sq_kilometer') / landarea) * 100, 2) - 100 "Difference Between Actual and Calculated Land Area as Percentage (%)"
FROM federal_elec_district;


-- Query 2: Calculate the area of the provinces (based on the data available).
-- Use the SDO_AREA function again to calculate the area and use your COGS_CONVERT_UNIT
-- function to convert the units to square kilometres. Give the province names in English
-- and French and the area in your answer.

SELECT
    b.prename "Province Name (English)",
    c.prfname "Province Name (French)",
    ROUND(SUM(COGS_CONVERT_UNIT(SDO_GEOM.SDO_AREA(a.geometry, 0.005), 'sq_meter', 'sq_kilometer')), 2) "Total Area of Province (Calculated, Sq Km)"
FROM federal_elec_district a
JOIN province_name_eng b ON a.pruid = b.pruid
JOIN province_name_fr c ON a.pruid = c.pruid
GROUP BY b.prename, c.prfname;