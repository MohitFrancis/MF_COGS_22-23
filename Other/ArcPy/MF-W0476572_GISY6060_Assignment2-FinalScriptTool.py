'''
Program:    MF-W0476572_GISY6060_Assignment2.py
Programmer: Mohit Francis
Date:       07 February 2023
Purpose:    GISY 6060 - Assignment 2 - Geoprocessing Script
            Creates random samples (number of samples determined by user)
            within the Annapolis County forest layer to determine the average
            percentage of a forest stand occupied by leading White Spruce (WS)
            and/or Black Spruce (BS) trees.
'''

## Import libraries.
import arcpy
import random

## Activate overwrite mode to overwrite all settings and created feature classes.
arcpy.env.overwriteOutput = True

## Set-up work space variables.
currWS = arcpy.GetParameterAsText(0)
currGDB = arcpy.GetParameterAsText(1)

## Set current ArcGIS work space where output and reads will occur.
arcpy.env.workspace = currWS

## Describe the forestry data set.
forestFeatClass = arcpy.GetParameterAsText(2)
desc = arcpy.Describe(forestFeatClass)

## Extract xmin, ymin, xmax, ymax values from Describe.
forXMin = int(desc.extent.XMin)
forYMin = int(desc.extent.YMin)
forXMax = int(desc.extent.XMax)
forYMax = int(desc.extent.YMax)

## Create a feature class to store X,Y random point samples.
out_path = arcpy.GetParameterAsText(1)
out_name = "randomPointSamples"
geometry_type = "POINT"
fcSpatialReference = desc.spatialReference
fcPoint = out_path + "/" + out_name

## Set spatial reference for new feature class using spatial reference from Describe object property.
arcpy.management.CreateFeatureclass(out_path, out_name, geometry_type, "", "", "", fcSpatialReference)

## Create empty list to store the X,Y coordinates of random sample points and the attributes of each sampled tree species.
listSpecies = []

## Create counter and sum of percentage variables before loop starts.
countSpecies1 = 0
countSpecies2 = 0
totalCount = 0
percentSpecies1 = 0
percentSpecies2 = 0
totalPercent = 0

## Allow user to enter the number of random samples needed.
numOfUserSamples = int(arcpy.GetParameterAsText(3))

## Generate the random samples, making sure to collect the number of samples requested.
while totalCount < numOfUserSamples:
    
    ## Generate random X,Y coordinate pairs.
    XCoord = random.randrange(forXMin, forXMax)
    YCoord = random.randrange(forYMin, forYMax)

    ## Create Insert Cursor.
    addPoint = arcpy.da.InsertCursor(fcPoint, ["SHAPE@XY"])

    ## Add points to feature class.
    xy = (XCoord,YCoord)
    addPoint.insertRow([xy])

    ## Delete Cursor.
    del addPoint

    ## Select by Location the forest polygons which intersect with the coordinates in the list of samples.
    ## I.e. select only the points within layer extent which 'touch' forest polygons.
    fcForest = forestFeatClass
    forestPolyLayer = arcpy.MakeFeatureLayer_management(fcForest, "forestpolylayer")
    forestPolySelection = arcpy.management.SelectLayerByLocation(forestPolyLayer, 'INTERSECT',fcPoint)

    ## Check to see the number of selected forest polygons.
    countOfPolys = int(arcpy.GetCount_management(forestPolySelection).getOutput(0))

    ## If a polygon is selected.
    if countOfPolys == 1:

        ## Create a Search Cursor to access the polygon's attributes.
        forestPolyCursor = arcpy.SearchCursor(forestPolySelection, fields = "MAPSTAND;SP1;SP1P;Shape_Area")

        ## Iterate through records selected by Search Cursor.
        for row in forestPolyCursor:

            ## If the user inputted species codes are in the Search Cursor:
            if row.getValue('SP1') == 'WS':

                ## Increment count of number of polygons of that species, the total number of species correctly sampled, and sum the forest tree stand percentage per species and overall.
                countSpecies1 += 1
                totalCount += 1
                percentSpecies1 += row.getValue('SP1P')
                totalPercent += row.getValue('SP1P')

                ## Let the user know Species 1 was found. Outputs to ArcGIS Pro Message screen.
                arcpy.AddMessage("White Spruce selected!")

                ## Add the UTM X Y coordinates, the sample location map stand, species code, tree stand percentage, and polygon shape area to the empty list.
                listSpecies.append((totalCount, str(XCoord) + ', ' + str(YCoord), row.getValue('MAPSTAND'), row.getValue('SP1'), row.getValue('SP1P'), row.getValue('Shape_Area')))    
                
            elif row.getValue('SP1') == 'BS':

                ## Increment count of number of polygons of that species, the total number of species correctly sampled, and sum the forest tree stand percentage per species and overall.
                countSpecies2 += 1
                totalCount += 1
                percentSpecies2 += row.getValue('SP1P')
                totalPercent += row.getValue('SP1P')

                ## Let the user know Species 2 was found. Outputs to ArcGIS Pro Message screen.
                arcpy.AddMessage("Black Spruce selected!")

                ## Add the UTM X Y coordinates, the sample location map stand, species code, tree stand percentage, and polygon shape area to the empty list.
                listSpecies.append((totalCount, str(XCoord) + ', ' + str(YCoord), row.getValue('MAPSTAND'), row.getValue('SP1'), row.getValue('SP1P'), row.getValue('Shape_Area')))

        ## Delete the random points before creating another random point.
        with arcpy.da.UpdateCursor(fcPoint, "*") as pointCursor:
            for row in pointCursor:
                pointCursor.deleteRow()
        del pointCursor

## Once the total number of samples required for each tree species is reached, display this message to ArcGIS Pro Message screen.
if totalCount == numOfUserSamples:
    arcpy.AddMessage("Sampling complete. Report ready!")

## Allow the user to select a name for the report file (optional, will otherwise use default name for the report).
reportFileName = arcpy.GetParameterAsText(4)
reportFileExt = '.txt'

## Write to file the results of the script, with specified path and file name and headers.
with open (currWS + "\\" + reportFileName + reportFileExt, "w") as currOutFile:
    currOutFile.write("\t\t\t\t\t   REPORT OF RANDOM SAMPLES TAKEN\n\n")
    currOutFile.write("===================================================================================================================\n")

## Only append to file any of the following if any locations containing Species 1 or Species 2 were sampled - this will generally happen.
if totalCount > 0:

    ## Append to file the following headers.
    with open (currWS + "\\" + reportFileName + reportFileExt, "a") as currOutFile:
        currOutFile.write("LIST OF RANDOM SAMPLES TAKEN\n")
        currOutFile.write("===================================================================================================================\n\n")
        currOutFile.write("Sample |  X,Y Coordinates  |  Map Stand  |  Leading Species  |  Stand Cover Percentage  |    Stand Area\n")
        currOutFile.write("  No.  |     (UTM 20 T)    |             |       (SP1)       |          (SP1P, %)       | (Square Metres)\n")

    ## Append to file the location, species code and tree stand percentage of each random sample of Species 1.
    for records in listSpecies:
        with open (currWS + "\\" + reportFileName + reportFileExt, "a") as currOutFile:
            currOutFile.write("\n{:^7d}   {}    {:^5s}\t\t {:^7s}\t\t {:^5d}\t\t      {:^.2f}\n".format(records[0], records[1], records[2], records[3], records[4], records[5]))

    ## Append to file the total number of samples taken per species and the overall count. Also append the headers of the next section of the report.
    with open (currWS + "\\" + reportFileName + reportFileExt, "a") as currOutFile:
        currOutFile.write("\n===================================================================================================================\n")
        currOutFile.write("NUMBER OF RANDOM SAMPLES PER SPECIES\n")
        currOutFile.write("===================================================================================================================\n\n")
        currOutFile.write("{} samples were taken per White Spruce (WS) species.\n".format(countSpecies1))
        currOutFile.write("{} samples were taken per Black Spruce (BS) species.\n\n".format(countSpecies2))
        currOutFile.write("A total number of {} sample(s) was taken for both Black Spruce (BS) and White Spruce (WS) species.\n".format(totalCount))
        currOutFile.write("\n===================================================================================================================\n")
        currOutFile.write("AVERAGE FOREST STAND COVER PERCENTAGE PER SPECIES\n")
        currOutFile.write("===================================================================================================================\n\n")

    ## An average (sum divided by total) cannot be calculated if the total is 0.
    ## Therefore, append to file the following statement if the average can be calculated.
    if countSpecies1 > 0:
        with open(currWS + "\\" + reportFileName + reportFileExt, "a") as currOutFile:
            currOutFile.write("The average percentage of a forest stand occupied by White Spruce (WS) trees was {:.2f} %.\n".format(percentSpecies1 / countSpecies1))

    ## Otherwise, append to file this statement if the average cannot be calculated.
    else:
        with open(currWS + "\\" + reportFileName + reportFileExt, "a") as currOutFile:
            currOutFile.write("Since {} White Spruce (WS) trees were sampled, the average percentage of the forest stand covered by White Spruce trees cannot be calculated.\n".format(countSpecies1))

    ## Append to file the following statement if the average can be calculated.
    if countSpecies2 > 0:
        with open(currWS + "\\" + reportFileName + reportFileExt, "a") as currOutFile:
            currOutFile.write("The average percentage of a forest stand occupied by Black Spruce (BS) trees was {:.2f} %.\n".format(percentSpecies2 / countSpecies2))

    ## Otherwise, append to file this statement if the average cannot be calculated.
    else:
        with open(currWS + "\\" + reportFileName + reportFileExt, "a") as currOutFile:
            currOutFile.write("Since {} Black Spruce (BS) trees were sampled, the average percentage of the forest stand covered by Black Spruce trees could not be calculated.\n".format(countSpecies2))

    ## This portion of the code will usually run since the total number of samples will usually be greater than 0. Therefore the following statement will generally append to file at the end.
    with open(currWS + "\\" + reportFileName + reportFileExt, "a") as currOutFile:
        currOutFile.write("\nThe average percentage of a forest stand occupied by Black Spruce (BS) and White Spruce (WS) trees was {:.2f} %.\n".format(totalPercent / totalCount))

## In the event Species 1 or 2 were not sampled (i.e. total number of samples is 0), then append to file the following statement, and ask the user to try again.
else:
    with open (currWS + "\\" + reportFileName + reportFileExt, "a") as currOutFile:
        currOutFile.write("\nNo random samples of specified tree species were taken. Please try again.")
