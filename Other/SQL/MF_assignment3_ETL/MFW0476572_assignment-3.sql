/*
  Program:    MFW0476572_assignment-3.sql
  Programmer: Mohit Francis - W0476572
  Class:      GISY 6021
  Date:       19 April 2023
  Purpose:    Oracle Spatial - Creating Tables containing geometry data,
              Loading Data using Python's OracleDB module,
              Inserting Geometry Metadata,
              Creating Spatial Indices on geometry columns,
              Querying data using spatial queries and operations.
*/



-- **********************
-- Creating Tables and Constraints
-- **********************


-- Table for Canadian populated places.
-- Create PRIMARY KEY constraint on cgndb_id.
-- Note that this table has a SDO_GEOMETRY column (Point).
CREATE TABLE   populated_place 
    (
    cgndb_id   VARCHAR2(5),
    geo_name   VARCHAR2(100),
    code       VARCHAR2(4),
    centroid   SDO_GEOMETRY,
    CONSTRAINT populated_place_cgndb_id_pk PRIMARY KEY (cgndb_id)
    );


-- Table for Canadian provinces.
-- Create PRIMARY KEY constraint for this table on
-- arbitrarily created id column which auto-increments.
-- Note that this table has a SDO_GEOMETRY column (Polygon).
CREATE TABLE province 
    (
    id          NUMBER GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),
    name        VARCHAR2(40),
    border      SDO_GEOMETRY,
    CONSTRAINT  province_id_pk PRIMARY KEY (id)
    );


-- Table for Canadian airports.
-- Create PRIMARY KEY constraint on iata.
-- Note that this table has a SDO_GEOMETRY column (Point).
CREATE TABLE   airport
    (
    iata       VARCHAR2(4),
    icao       VARCHAR2(4),
    name       VARCHAR2(100),
    city       VARCHAR2(100),
    location   SDO_GEOMETRY,
    CONSTRAINT airport_icao_pk PRIMARY KEY (icao)
    );



-- **********************
-- Spatial Metadata
-- **********************


-- Insert geometry metadata of Centroid column of Populated_Place table.
-- Use specified lower and upper bounds and tolerance for each point.
-- Use specified SRID of 4269.
INSERT INTO
    user_sdo_geom_metadata
VALUES
        (
        'populated_place',
        'centroid',
        sdo_dim_array
            (
            sdo_dim_element('X', 7000000, 9000000, 0.00000005),
            sdo_dim_element('Y', 1000000, 1800000, 0.00000005)
            ),
        4269
        );


-- Insert geometry metadata of Border column of Province Table.
-- Use specified lower and upper bounds and tolerance for each point in array.
-- Use specified SRID of 3347.
-- This different SRID should not cause any issues when performing the spatial queries.
INSERT INTO
    user_sdo_geom_metadata
VALUES
        (
        'province',
        'border',
        sdo_dim_array
            (
            sdo_dim_element('X', 7000000, 9000000, 0.00000005),
            sdo_dim_element('Y', 1000000, 1800000, 0.00000005)
            ),
        3347
        );


-- Insert geometry metadata of Location column of Airport table.
-- Use specified lower and upper bounds and tolerance for each point.
-- Use specified SRID of 4269.
INSERT INTO
    user_sdo_geom_metadata
VALUES
        (
        'airport',
        'location',
        sdo_dim_array
            (
            sdo_dim_element('X', 7000000, 9000000, 0.00000005),
            sdo_dim_element('Y', 1000000, 1800000, 0.00000005)
            ),
        4269
        );



-- **********************
-- Creating Spatial Indices
-- **********************


-- Create a spatial index for the Populated_Place table on the Centroid column.
CREATE INDEX
    populated_place_centroid_idx
ON
    populated_place(centroid)
INDEXTYPE IS
    mdsys.spatial_index_v2
PARAMETERS
    (
        'layer_gtype=POINT'
    );

-- Create a spatial index for the province table on the border column.
CREATE INDEX
    province_border_idx
ON
    province(border)
INDEXTYPE IS
    mdsys.spatial_index_v2
PARAMETERS
    (
        'layer_gtype=POLYGON'
    );

-- Create a spatial index for the airport table on the location column.
CREATE INDEX
    airport_location_idx
ON
    airport(location)
INDEXTYPE IS
    mdsys.spatial_index_v2
PARAMETERS
    (
        'layer_gtype=POINT'
    );



-- **********************
-- Querying the Data
-- **********************


/*
Query 1:    Identify the two airports that are closest to one another
            and give the distance in kilometres.
            --What sort of aircraft would be required to fly
              between these two airports?
*/


-- I use a common table expression to create a temporary table called Close_Airports.
-- I modified the starter code provided for Query 5, creating a table of routes by
-- joining every airport to every other airport except itself, without duplicating routes.
-- I modified the starter code by also including the airport names and airport geometries
-- of the from and to airports. I use the SDO_GEOM.SDO_DISTANCE to calculate the distance
-- between the from and to airports in km, ordering by distance to find the
-- the airports that are closest to each other.
WITH close_airports AS
    (
    SELECT
        fa.icao AS from_airport_icao,
        fa.name AS from_airport_name,
        fa.location AS from_airport_location,
        ta.icao AS to_airport_icao,
        ta.name AS to_airport_name,
        ta.location AS to_airport_location
    FROM
        airport fa 
    INNER JOIN
        airport ta 
    ON
        fa.icao < ta.icao
    ORDER BY
        fa.icao, ta.icao
    )
SELECT
    c.from_airport_name AS "Departure Airport",
    c.to_airport_name AS "Arrival Airport",
    ROUND(
            SDO_GEOM.SDO_DISTANCE(  c.from_airport_location,
                                    c.to_airport_location,
                                    0.005,
                                    'unit=KM'),
            2) AS Distance
FROM
    close_airports c
ORDER BY
    Distance ASC
FETCH NEXT 1 ROWS ONLY;


/* Query 1 results:

A helicopter is best for flying between these two airports,
but imagine how fast a Concorde would fly this route.

DEPARTURE AIRPORT ARRIVAL AIRPORT         DISTANCE 
----------------- ----------------------- -------- 
Vancouver Harbour Vancouver International    11.08 
*/



/*
Query 2:    Identify the two airports that are furthest apart and
            give the distance in kilometres.
*/


-- I repeat the process used for Query 1, using a CTE to create a temporary table called Far_Airports.
-- I modified the starter code provided for Query 5, creating a table of routes by
-- joining every airport to every other airport except itself, without duplicating routes.
-- I modified the starter code by also including the airport names and airport geometries
-- of the from and to airports. I use the SDO_GEOM.SDO_DISTANCE to calculate the distance
-- between the from and to airports in km, ordering by distance to find the
-- the airports that are furthest apart.
WITH far_airports AS
    (
    SELECT
        fa.icao AS from_airport_icao,
        fa.name AS from_airport_name,
        fa.location AS from_airport_location,
        ta.icao AS to_airport_icao,
        ta.name AS to_airport_name,
        ta.location AS to_airport_location
    FROM
        airport fa 
    INNER JOIN
        airport ta 
    ON
        fa.icao < ta.icao
    ORDER BY
        fa.icao, ta.icao
    )
SELECT
    f.from_airport_name AS "Departure Airport",
    f.to_airport_name AS "Arrival Airport",
    ROUND(
            SDO_GEOM.SDO_DISTANCE(  f.from_airport_location,
                                    f.to_airport_location,
                                    0.005,
                                    'unit=KM'),
            2) AS Distance
FROM
    far_airports f
ORDER BY
    Distance DESC
FETCH NEXT 1 ROWS ONLY;


/* Query 2 results:

DEPARTURE AIRPORT ARRIVAL AIRPORT DISTANCE 
----------------- --------------- -------- 
Prince Rupert     St John's Intl   5228.66 
*/



/*
Query 3:    Tabulate the number of airports in each province.
            --Use a spatial query in order to complete this task.
*/


-- I use the SDO_RELATE('mask=INSIDE') spatial query to spatially join the Airport
-- and Province tables, in order to count all airports inside each province.
-- The results are listed by the number of airports in each province.
SELECT
    p.name AS "Province",
    COUNT(a.location) AS "Number of Airports in each Province"
FROM
    airport a,
    province p
WHERE
    SDO_RELATE(a.location, p.border, 'mask=INSIDE') = 'TRUE'
GROUP BY
    p.name
ORDER BY
    COUNT(a.location) DESC;


/* Query 3 Results:

PROVINCE                  NUMBER OF AIRPORTS IN EACH PROVINCE 
------------------------- ----------------------------------- 
British Columbia                                           23 
Ontario                                                    18 
Quebec                                                     15 
Alberta                                                    14 
Manitoba                                                    5 
Saskatchewan                                                4 
Newfoundland and Labrador                                   4 
New Brunswick                                               3 
Nova Scotia                                                 1 
Prince Edward Island                                        1 
*/



/*
Query 4:    Which populated place has the most airports within 20 km
            and what are the airports within 20 km of this place?
*/


-- I first use the SDO_WITHIN_DISTANCE convenience operator to spatially join the
-- Populated_Place and Airport tables in order to count the number of
-- airports within a 20 km radius of each populated place.
-- I return the place with the most airports in its 20 km radius.
SELECT
    p.geo_name AS "Place Name",
    COUNT(a.location) as "Number of Airports within 20 Kilometres of Place"
FROM
    populated_place p,
    airport a
WHERE
    sdo_within_distance(p.centroid, a.location, 'distance=20 unit=KM') = 'TRUE'
GROUP BY
    p.geo_name
ORDER BY
    COUNT(a.location) DESC
FETCH NEXT 1 ROWS ONLY;


/* Query 4, Part 1 results:

PLACE NAME      NUMBER OF AIRPORTS WITHIN 20 KILOMETRES OF PLACE
--------------- ------------------------------------------------ 
New Westminster                                                4 
*/


-- Next, I again use the SDO_WITHIN_DISTANCE convenience operator to spatially join the
-- Populated_Place and Airport tables in order to return list the names of the airports
-- within 20 km of New Westminster.
SELECT
    p.geo_name AS "Place Name",
    a.name AS "Names of Airports within 20 Kilometres of Place"
FROM
    populated_place p,
    airport a
WHERE
    sdo_within_distance(p.centroid, a.location, 'distance=20 unit=KM') = 'TRUE'
AND
    p.geo_name = 'New Westminster';


/* Query 4, Part 2 results:

PLACE NAME      NAMES OF AIRPORTS WITHIN 20 KILOMETRES OF PLACE 
--------------- ----------------------------------------------- 
New Westminster Vancouver Harbour                               
New Westminster Vancouver International                         
New Westminster Pitt Meadows                                    
New Westminster Boundary Bay    
*/



/*
Query 5:    Tabulate the routes between airports that
            fly within 5 km of 45 or more populated places.
            --A route is a linear geometry between airports.
            --Assume that each airport is connected directly to every other airport in the data set.
            --You may want to create an additional table to store flight routes.
            --Show the following columns in the report:
                    ---From airport name.
                    ---To airport name.
                    ---Count of populated places within 5 km of the route.
*/


/* Starter code provided for Query 5:

SELECT
    fa.icao AS from_airport_icao, 
    ta.icao AS to_airport_icao
FROM
    airport fa 
INNER JOIN
    airport ta 
ON
    fa.icao < ta.icao
ORDER BY
    fa.icao, ta.icao;
*/


-- Create additional table to store route information.
-- A route is the straight line joining two airports.
-- Create COMPOSITE PRIMARY KEY on both icao columns in table.
-- Create FOREIGN KEYS as both icao columns in Route table
-- reference the same icao column in Airport table.
-- There are additional columns to store the names of each airport,
-- the name of the route, and the line geometry derived from the from
-- and to airport locations of the route.
-- Note that this table has a SDO_GEOMETRY column (Line).
CREATE TABLE                route 
    (
    from_airport_icao       VARCHAR2(4),
    from_airport_name       VARCHAR2(100),
    to_airport_icao         VARCHAR2(4),
    to_airport_name         VARCHAR2(100),
    route_name              VARCHAR2(200),
    route_line              SDO_GEOMETRY,
    CONSTRAINT              route_from_airport_icao_to_airport_icao_pk PRIMARY KEY (from_airport_icao, to_airport_icao),
    CONSTRAINT              airportTOroute_from_airport_icao_fk FOREIGN KEY (from_airport_icao) REFERENCES airport(icao),
    CONSTRAINT              airportTOroute_to_airport_icao_fk FOREIGN KEY (to_airport_icao) REFERENCES airport(icao)
    );


-- I populate Route table with list of routes using the modified starter code provided for this query.
-- A route comprises each airport joined to every other airport except itself.
-- It does not duplicate routes, e.g CYAM -> CYAV is recorded but not CYAV -> CYAM.
-- I modified the starter code provided for this query by also including the
-- airport names; by populating the Route_Name column by concatenating
-- the names of the from and to airports; and by calculating the line geometry of the route
-- by using the geometries of the from and to airport locations as the start and end points of the route line.
-- While this table is denormalised, it is convenient for the purposes of answering this query.
INSERT INTO         route   
                (
                    from_airport_icao,
                    from_airport_name,
                    to_airport_icao,
                    to_airport_name,
                    route_name,
                    route_line
                )
    SELECT
        fa.icao AS from_airport_icao,
        fa.name AS from_airport_name,
        ta.icao AS to_airport_icao,
        ta.name AS to_airport_name,
        fa.name || ' to ' || ta.name AS route_name,
        sdo_geometry
            (
                    2002,
                    4269,
                    NULL,
                    sdo_elem_info_array (1, 2, 1),
                    sdo_ordinate_array (fa.location.sdo_point.x,
                                         fa.location.sdo_point.y,
                                         ta.location.sdo_point.x,
                                         ta.location.sdo_point.y)
            ) AS route_line
    FROM
        airport fa 
    INNER JOIN
        airport ta 
    ON
        fa.icao < ta.icao
    ORDER BY
        fa.icao, ta.icao;


-- Insert geometry metadata of Route_Line column of Route table.
-- Use specified lower and upper bounds and tolerance for each point.
-- Use specified SRID of 4269, which is the same as SRID of the Location
-- column in the Airport table.
INSERT INTO
    user_sdo_geom_metadata
VALUES
        (
        'route',
        'route_line',
        sdo_dim_array
            (
            sdo_dim_element('X', 7000000, 9000000, 0.00000005),
            sdo_dim_element('Y', 1000000, 1800000, 0.00000005)
            ),
        4269
        );


-- Create a spatial index for the Route table on the Route_Line column.
CREATE INDEX
    route_route_line_idx
ON
    route(route_line)
INDEXTYPE IS
    mdsys.spatial_index_v2
PARAMETERS
    (
        'layer_gtype=LINE'
    );


-- This query is essentially asking the number of places within 5 km of the route,
-- along the entire length of the route. I use the SDO_WITHIN_DISTANCE convenience
-- operator to spatially join the Populated_Place and Route tables in order to
-- return the start and end airports of routes flying over 45 or more places.
SELECT
    r.from_airport_name AS "Departure Airport",
    r.to_airport_name AS "Arrival Airport",
    COUNT(p.centroid) AS "Number of Places Within 5 km of Route Along Entire Length of Route"
FROM
    route r,
    populated_place p
WHERE
    sdo_within_distance(r.route_line, p.centroid, 'distance=5 unit=KM') = 'TRUE'
HAVING
    COUNT(p.centroid) >= 45
GROUP BY
    r.from_airport_name,
    r.to_airport_name
ORDER BY
    COUNT(p.centroid) DESC;


/* Query 5 Results:

DEPARTURE AIRPORT                             ARRIVAL AIRPORT         NUMBER OF PLACES WITHIN 5 KM OF ROUTE ALONG ENTIRE LENGTH OF ROUTE 
--------------------------------------------- ----------------------- ------------------------------------------------------------------
Gander International                          London                                                                                  58 
Windsor                                       Gander International                                                                    53 
Montréal-Pierre Elliott Trudeau International St John's Intl                                                                          49 
Gander International                          Toronto City Centre                                                                     48 
Deer Lake                                     Hamilton                                                                                46 
Nanaimo                                       Montréal/St-Hubert                                                                      46 
Oshawa                                        Gander International                                                                    46 
Montréal/St-Hubert                            Vancouver International                                                                 45   
*/