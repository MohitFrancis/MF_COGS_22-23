'''
    Program   : MF_W0476572_placesWorld-2ndSubmission.py
    Programmer: Mohit Francis
    Date      : 24 November 2022
    Purpose   : PROG 5000: Assignment 2 (2nd Submission) - Load point shapefile as layer.
                Allow user to select points/places, extract X,Y coordinates,
                determine North/South hemisphere and East/West hemisphere designation,
                count points/places and populations of places in each quadrant,
                determine places in selection with highest and lowest populations,
                and write to file a report containing the above information.
                If user does not manually select any number of points, create
                report file for all points in layer.
'''

## ------------------------------------------------ Import libraries. --------------------------------------------------
from qgis.PyQt.QtCore import QVariant
import os

## ---- Function getNSHemi(): Classify point as being either North or South of the Equator. ----------------------------
## -------------------------------------- Store classification in newly created field NSHemi. --------------------------
def getNSHemi(currLayer, idxNSHemi):

    ## Make PlacesOfTheWorld the current, working layer.
    currLayer = qgis.utils.iface.activeLayer()

    ## If user has manually selected features using Select tool
    ## then selected features are assigned to selFeatures. If user
    ## has not manually selected any features using Select tool, then select all
    ## features and assign to selFeatures. 
    if currLayer.selectedFeatureCount() > 0:
        selFeatures = currLayer.getSelectedFeatures()
    else:
        selFeatures = currLayer.selectAll()
    
    ## Result of if statement is permanently assigned to selFeatures.
    selFeatures = currLayer.getSelectedFeatures()
    
    ## Start edit session:
    ## Iterate through selected features, extract geometry,
    ## separate X,Y coordinates and assign to separate variables.
    currLayer.startEditing()
    for features in selFeatures:
        id = features.id()
        geom = features.geometry()
        xCoord = geom.asPoint().x()
        yCoord = geom.asPoint().y()
    
    ## If Y (latitude) is greater than or equal to 0, classify point as North.
    ## If Y is less than 0, classify point as South.
    ## Add classification to newly created NSHemi field in attribute table.
        if yCoord >= 0:
            attr_value = {idxNSHemi : 'North'}
            currLayer.dataProvider().changeAttributeValues({id : attr_value})
        else:
            attr_value = {idxNSHemi : 'South'}
            currLayer.dataProvider().changeAttributeValues({id : attr_value})

    ## Commit the addition of data.
    currLayer.commitChanges()

## ---- Subfunction getEWHemi(): Classify point as being either East or West of Prime Meridian. ------------------------
## -------------------------------------- Store classification in newly created field EWHemi. --------------------------
def getEWHemi(currLayer, idxEWHemi):

    ## Make PlacesOfTheWorld the current, working layer.
    currLayer = qgis.utils.iface.activeLayer()

    ## If user has manually selected features using Select tool
    ## then selected features are assigned to selFeatures. If user
    ## has not manually selected any features using Select tool, then select
    ## all features and assign to selFeatures.
    if currLayer.selectedFeatureCount() > 0:
        selFeatures = currLayer.getSelectedFeatures()
    else:
        selFeatures = currLayer.selectAll()
    
    ## Result of if statement is permanently assigned to selFeatures.
    selFeatures = currLayer.getSelectedFeatures()

    ## Start edit session:
    ## Iterate through selected features, extract geometry,
    ## separate X,Y coordinates and assign to separate variables.
    currLayer.startEditing()
    for features in selFeatures:
        id = features.id()
        geom = features.geometry()
        xCoord = geom.asPoint().x()
        yCoord = geom.asPoint().y()
        
    ## If X (longitude) is greater than or equal to 0, classify point as East.
    ## If X is less than 0, classify point as West.
    ## Add classification to newly created EWHemi field in attribute table.
        if xCoord >= 0:
            attr_value = {idxEWHemi : 'eastern'}
            currLayer.dataProvider().changeAttributeValues({id : attr_value})
        else:
            attr_value = {idxEWHemi : 'western'}
            currLayer.dataProvider().changeAttributeValues({id : attr_value})

    ## Commit the addition of data.
    currLayer.commitChanges()

## ------------------------------------------------- Function main(). --------------------------------------------------
def main():

## ---- Add new fields to attribute table of current layer. ------------------------------------------------------------

    ## Make PlacesOfTheWorld the current, working layer.
    currLayer = qgis.utils.iface.activeLayer()

    ## Check to see if we can update attribute table of PlacesOfTheWorld.
    caps = currLayer.dataProvider().capabilities()
    currLayer.updateFields()

    ## Add the coordinate and classification fields to the attribute table of the PlacesOfTheWorld shapefile.
    if caps & QgsVectorDataProvider.AddAttributes:

        ## Store coordinates as decimals, store hemisphere classifications as strings.
        res = currLayer.dataProvider().addAttributes([
            QgsField("XCoord", QVariant.Double),
            QgsField("YCoord", QVariant.Double),
            QgsField("NSHemi", QVariant.String),
            QgsField("EWHemi", QVariant.String)])

    ## Commit the addition of fields.
    currLayer.updateFields()

## ---- Extract X,Y Coordinates. Store coordinates separately in newly created fields XCoord and YCoord. --------------

    ## Make PlacesOfTheWorld the current, working layer.
    currLayer = qgis.utils.iface.activeLayer()

    ## If user has manually selected features using
    ## Select tool, then selected features are assigned to selFeatures. If user
    ## has not manually selected any features using Select tool, then select all
    ## features and assign to selFeatures.
    if currLayer.selectedFeatureCount() > 0:
        selFeatures = currLayer.getSelectedFeatures()
    else:
        selFeatures = currLayer.selectAll()
    
    ## Result of if statement is permanently assigned to selFeatures.
    selFeatures = currLayer.getSelectedFeatures()

    ## Start an edit session to update attribute values for each point.
    ## Extract point geometry, separate X and Y coordinates.
    ## For all places, assign X coordinates to newly created XCoord field in attribute table,
    ## assign Y coordinates to newly created YCoord field in attribute table.
    currLayer.startEditing()
    idxX = currLayer.fields().indexFromName('XCoord')
    idxY = currLayer.fields().indexFromName('YCoord')
    for features in selFeatures:
        id = features.id()
        geom = features.geometry()
        xCoord = geom.asPoint().x()
        yCoord = geom.asPoint().y()
        attr_value = {idxX : xCoord, idxY : yCoord}
        currLayer.dataProvider().changeAttributeValues({id : attr_value})

    ## Commit the addition of data.
    currLayer.commitChanges()

## ---- Separate selected places of world into world's four quadrants based on hemisphere designation. ---------------
## ---- Count number of places in each quadrant, sum populations of places in each quadrant. -------------------------

    ## Make PlacesOfTheWorld the current, working layer.
    ## Have to restate to get called functions to work.
    currLayer = qgis.utils.iface.activeLayer()

    ## Run the two classification functions
    ## passing in the current layer and the
    ## position of the classification attributes.
    idxNSHemi = currLayer.fields().indexFromName('NSHemi')
    idxEWHemi = currLayer.fields().indexFromName('EWHemi')
    getNSHemi(currLayer, idxNSHemi)
    getEWHemi(currLayer, idxEWHemi)

    ## Restate selected features to allow loop to work.
    selFeatures = currLayer.getSelectedFeatures()

    ## Initialise sum and count variables for each quadrant to zero, before the start of the loop.
    sumNEpop = 0
    countNEplaces = 0
    sumNWpop = 0
    countNWplaces = 0
    sumSEpop = 0
    countSEplaces = 0
    sumSWpop = 0
    countSWplaces = 0

    ## Loop through the selected features.
    for features in selFeatures:
        
        ## Places North and East of (0,0) are counted, and their areas are summed.
        if features['NSHemi'] == 'North' and features['EWHemi'] == 'eastern':
            countNEplaces += 1
            sumNEpop += features['pop_max']
            
        ## Places North and West of (0,0) are counted, and their areas are summed.
        elif features['NSHemi'] == 'North' and features['EWHemi'] == 'western':
            countNWplaces += 1
            sumNWpop += features['pop_max']
            
        ## Places South and East of (0,0) are counted, and their areas are summed.
        elif features['NSHemi'] == 'South' and features['EWHemi'] == 'eastern':
            countSEplaces += 1
            sumSEpop += features['pop_max']
        
        ## Places South and West of (0,0) are counted, and their areas are summed.
        else:
            countSWplaces += 1
            sumSWpop += features['pop_max']

## ---- Out of the selected places, determine the places with --------------------------------------------------
## ---- the highest and lowest populations; return the place name, ---------------------------------------------
## ---- population, and quadrant designation of each. ----------------------------------------------------------

    ## Restate selected features to allow next loop to work.
    selFeatures = currLayer.getSelectedFeatures()

    ## Create empty list to store (list of) attributes of (list of) selected features as list of lists.
    listSelFeatures = []
    for features in selFeatures:
        ## Each row of attribute table stored as list in attRows - different rows are different lists.
        ## Each list in attRow appended to list of selected features.
        attRows = features.attributes()
        listSelFeatures.append(attRows)

    ## Before loop, initialise minimum and maximum population values to the first population value
    ## of the first selected place. Initialise empty strings for the place names and quadrant designations.
    minPop = listSelFeatures[0][1]
    maxPop = listSelFeatures[0][1]
    maxPlace = ""
    minPlace = ""
    maxQuadrant = ""
    minQuadrant = ""

    ## For each feature in list of features, assess the following:
    for i in listSelFeatures:

        ## If population of current place being assessed is greater than the
        ## previous maximum population, then current population
        ## becomes new maximum population. The place name, plus the hemisphere
        ## designations are added to empty string variables.        
        if i[1] > maxPop:
            maxPop = i[1]
            maxPlace = i[0]
            ## Potential NULL values in the NSHemi and EWHemi columns are not concatenated,
            ## i.e. NULL values for any points not initially selected.
            if i[4] and i[5] != NULL:
                maxQuadrant = i[4] + i[5]

        ## If population of current place being assessed is less than the
        ## previous minimum population, then current population
        ## becomes new minimum population. The place name, plus the hemisphere
        ## designations are added to empty string variables.
        ## NULL values in the NSHemi and EWHemi columns are not concatenated.
        if i[1] < minPop:
            minPop = i[1]
            minPlace = i[0]
            ## Potential NULL values in the NSHemi and EWHemi columns are not concatenated,
            ## i.e. NULL values for any points not initially selected.
            if i[4] and i[5] != NULL:
                minQuadrant = i[4] + i[5]

## ---- Write results to file. ----------------------------------------------------------------

    ## Using the "with" open file syntax, open a file to write a summary report of selected world places
    ## summarizing count and population values for each classification; the place names, quadrant designation
    ## and population values of places within selection with the highest and lowest populations.
    with open (r"c:\temp\MF_W0476572_worldplacesreport.txt", "w") as currOutFile:
        currOutFile.write("Report of Selected World Places\n")
        currOutFile.write("===========================================================================\n")
        currOutFile.write("{} Northeastern places have a total population of {}\n".format(countNEplaces, sumNEpop))
        currOutFile.write("{} Northwestern places have a total population of {}\n".format(countNWplaces, sumNWpop))
        currOutFile.write("{} Southeastern places have a total population of {}\n".format(countSEplaces, sumSEpop))
        currOutFile.write("{} Southwestern places have a total population of {}\n".format(countSWplaces, sumSWpop))
        currOutFile.write("===========================================================================\n")
        currOutFile.write("The {} place of {} has the highest population of {}\n".format(maxQuadrant, maxPlace, maxPop))
        currOutFile.write("The {} place of {} has the lowest population of {}\n".format(minQuadrant, minPlace, minPop))

## ---- Deleting coordinate and classification attributes from attribute table to make script re-runnable. ------------

    ## Make PlacesOfTheWorld the current, working layer.
    currLayer = qgis.utils.iface.activeLayer()

    ## Check to see if we can update attribute table of PlacesOfTheWorld.
    caps = currLayer.dataProvider().capabilities()
    currLayer.updateFields()

    ##  Delete the coordinate and classification fields from the attribute table of the PlacesOfTheWorld shapefile.
    if caps & QgsVectorDataProvider.DeleteAttributes:

        ## If the index number is -1, that means the index search
        ## didn't find the attribute. If index number is greater
        ## than -1, the position is returned.

        ## Determine index number of XCoord using field name.
        idxX = currLayer.fields().indexFromName('XCoord')
        if idxX > -1:
            res = currLayer.dataProvider().deleteAttributes([idxX])
            ## Update fields after deletion to refresh indices.
            currLayer.updateFields()

        ## Determine index number of YCoord using field name.
        idxY = currLayer.fields().indexFromName('YCoord')
        if idxY > -1:
            res = currLayer.dataProvider().deleteAttributes([idxY])
            ## Update fields after deletion to refresh indices.
            currLayer.updateFields()

        ## Determine index number of NSHemi using field name.
        idxNSHemi = currLayer.fields().indexFromName('NSHemi')
        if idxNSHemi > -1:
            res = currLayer.dataProvider().deleteAttributes([idxNSHemi])
            ## Update fields after deletion to refresh indices.
            currLayer.updateFields()

        ## Determine index number of EWHemi using field name.
        idxEWHemi = currLayer.fields().indexFromName('EWHemi')
        if idxEWHemi > -1:
            res = currLayer.dataProvider().deleteAttributes([idxEWHemi])
            ## Update fields after deletion to refresh indices..
            currLayer.updateFields()

## ------------------------------ Mainline: Start the script by invoking the main() function. --------------------------

main()
