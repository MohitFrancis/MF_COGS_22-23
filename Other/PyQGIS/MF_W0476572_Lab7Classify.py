'''
Program:    MF_W0476572_Lab7Classify.py
Programmer: Mohit Francis
Date:       08 November 2022
Purpose:    To classify polygons in forestry layer based on selection criteria.
'''

# Import libraries.
from qgis.PyQt.QtCore import QVariant
import os

###################################################################################
# Classify function:  Creates a selection set for each risk/classification factor
#                     and assigns a classification code and classification number 
#                     to the features.
################################################################################
def classify(workingLayer, idxClassNumb, idxClassCode):
    print("In classify function!")
    
    caps = workingLayer.dataProvider().capabilities()
    currFeatures = workingLayer.getFeatures()
   
    ############################################################################
    # ... Set classification to "HIGH" (100) suitability class for polygons 
    #     with leading species of Black Spruce ("BS") and Height
    #     over 6 metres.
    
    # Select polygon features based on attributes.
    selFeatures = workingLayer.selectByExpression('"SP1"=\'BS\' AND HEIGHT > 6',QgsVectorLayer.SetSelection)

    # Set colour of selected features.
    iface.mapCanvas().setSelectionColor( QColor("red") )
    
    # Get subset that contains all of the selected features.
    currSelection = workingLayer.selectedFeatures()
    
    # Start an edit session to update the attribute values.
    workingLayer.startEditing()
    for feature in currSelection:
        id = feature.id()
        if caps & QgsVectorDataProvider.ChangeAttributeValues:
                attrs = { idxClassNumb : 100 , idxClassCode : 'HIGH' }
                workingLayer.dataProvider().changeAttributeValues({ id : attrs })
        pass
    workingLayer.commitChanges()
    
    # ... End of classifying "HIGH" suitability.
    ############################################################################
    
    ############################################################################
    # Set classification to "MEDIUM" (50) suitability class for polygons 
    #     with leading species of Red Spruce ("RS") and Height
    #     over 6 metres.
    
    # Select polygon features based on attributes.
    selFeatures = workingLayer.selectByExpression('"SP1"=\'RS\' AND HEIGHT > 6',QgsVectorLayer.SetSelection)

    # Set colour of selected features.
    iface.mapCanvas().setSelectionColor( QColor("blue") )
    
    # Get subset that contains all of the selected features.
    currSelection = workingLayer.selectedFeatures()
    
    # Start an edit session to update the attribute values.
    workingLayer.startEditing()
    for feature in currSelection:
        id = feature.id()
        if caps & QgsVectorDataProvider.ChangeAttributeValues:
                attrs = { idxClassNumb : 50 , idxClassCode : 'MEDIUM' }
                workingLayer.dataProvider().changeAttributeValues({ id : attrs })
        pass
    workingLayer.commitChanges()

    # ... End of "MEDIUM" suitability classification.
    ############################################################################
    
    ############################################################################
    # Set classification to "LOW" (1) suitability class for polygons 
    #     with leading species of White Pine ("WP") and Height
    #     over 4 metres.
    
    # Select polygon features based on attributes.
    selFeatures = workingLayer.selectByExpression('"SP1"=\'WP\' AND HEIGHT > 4',QgsVectorLayer.SetSelection)

    # Set colour of selected features.
    iface.mapCanvas().setSelectionColor( QColor("yellow") )
    
    
    # Get subset that contains all of the selected features.
    currSelection = workingLayer.selectedFeatures()
    
    # Start an edit session to update the attribute values.
    workingLayer.startEditing()
    for feature in currSelection:
        id = feature.id()
        if caps & QgsVectorDataProvider.ChangeAttributeValues:
                attrs = { idxClassNumb : 1 , idxClassCode : 'LOW' }
                workingLayer.dataProvider().changeAttributeValues({ id : attrs })
        pass
    workingLayer.commitChanges()
    
    # ... End of "LOW" suitability classification.
    ############################################################################

##########################################################################################
# ... Summary function: Summarises the results of the classification by determining
#                       the number of polygons, and the total area of all of the polygons
#                       in the study area that match each classification.
##########################################################################################

def summary(currWorkingLayer, idxClassNumb,idxClassCode, idxShapeArea):
    print("In summary function!")
        
    # Create a selection set where the Class_Code has a value (i.e. Class_Code is not NULL),
    # or the Class_Numb is not equal to zero (0) (i.e. Class_Numb is > 0).
    # Select polygon features based on attributes.
    selFeatures = currWorkingLayer.selectByExpression('Class_Numb > 0', QgsVectorLayer.SetSelection)
    
    # Set colour of selected features.
    iface.mapCanvas().setSelectionColor( QColor("green") )
       
    # Get subset that contains all of the selected features.
    currSelection = currWorkingLayer.selectedFeatures()
        
    # Initialise sum and count variable to zero, before the start of the loop.
    sumClassHigh = 0
    countClassHigh = 0
    sumClassMedium = 0
    countClassMedium = 0
    sumClassLow = 0
    countClassLow = 0
    
    # Loop through the selection set keeping track of the following:
    for feature in currSelection:
        # If the feature belongs to the "HIGH" suitability:
            # Count of polygons with high class code.
            # Sum areas of the polygons in the high class code.
        if feature['Class_Code'] == 'HIGH':
            countClassHigh += 1
            sumClassHigh += feature[idxShapeArea]
        elif feature['Class_Code'] == 'MEDIUM':
        # Else if the feature belongs to the "MEDIUM" suitability:
            # Count polygons with medium class code.
            # Sum areas of the polygons in the medium class code.
            countClassMedium += 1
            sumClassMedium += feature[idxShapeArea]
        else:
        # Else if the feature belongs to the "LOW" suitability:
            # Count polygons with low class code.
            # Sum areas of the polygons in the low class code.
            countClassLow += 1
            sumClassLow += feature[idxShapeArea]

    #     Using the "with" open file syntax, open a file to write a summary
    #     report, summarizing count and area values for each classification
    #     (2 decimal places for area values).
    with open (r"c:\temp\data\SummaryReport.txt", "w") as currOutFile:        
        currOutFile.write("----------------------------HABITAT SUITABILITY SUMMARY REPORT----------------------------\n\n")
        currOutFile.write("The number of polygons classified HIGH are {}.\n".format(countClassHigh))
        currOutFile.write("The sum of areas of polygons classified HIGH are {:.2f} square metres.\n\n".format(sumClassHigh))
        currOutFile.write("The number of polygons classified MEDIUM are {}.\n".format(countClassMedium))
        currOutFile.write("The sum of areas of polygons classified MEDIUM are {:.2f} square metres.\n\n".format(sumClassMedium))
        currOutFile.write("The number of polygons classified LOW are {}.\n".format(countClassLow))
        currOutFile.write("The sum of areas of polygons classified LOW are {:.2f} square metres.\n\n".format(sumClassLow))
        currOutFile.write("----------------------------------------END REPORT----------------------------------------")

################################################################################
# Main function:  add shapefile to project and adds necessary classification
#                      attributes to the shapefile's attribute table.
################################################################################
def main():
        
    # Get list of layers.
    listOfMapLayers = QgsProject.instance().mapLayers()
    
    # If ANNAFOREST shapefile is already loaded, remove the layer.
    for lyr in listOfMapLayers.values():
        if lyr.name().upper() == 'ANNAFOREST':
            print("AnnaForest is currently loaded, now to remove")
            QgsProject.instance().removeMapLayer(lyr.id())
     
    # Add ANNAFOREST shapefile to the project.
    uri = r"c:\temp\data\annaForest.shp"
    vlayer = QgsVectorLayer(uri, "annaForest", "ogr")
    QgsProject.instance().addMapLayer(vlayer)

    # Make ANNAFOREST the working layer.
    currLayer = iface.activeLayer()

    # Check to see if we can update attributes of annaForest.
    caps = currLayer.dataProvider().capabilities()
    
    # Check if a particular capability is supported:
    if caps & QgsVectorDataProvider.ChangeAttributeValues:
        print('The layer supports ChangeAttributeValues')
    else:
        print('The layer DOES NOT supports ChangeAttributeValues')

    # Add classification attribute to annaForest attribute table.
    currLayer.updateFields()
    
    # Delete the classification attributes if they already exist
    # on the ANNAFOREST shapefile.
    if caps & QgsVectorDataProvider.DeleteAttributes:
        
        # Get the field names from the current layer.
        fields = currLayer.fields()
        # Determine their index numbers.
        idxClassNumb = fields.indexFromName('Class_Numb')
        idxClassCode = fields.indexFromName('Class_Code')
        
        # If the index number is -1, that means the index search
        # didn't find the attribute. If index number is greater
        # than -1, the position is returned.
        if idxClassCode > -1:
            print("Class code index is: ",idxClassCode)
            res = currLayer.dataProvider().deleteAttributes([idxClassCode])
      
        if idxClassNumb > -1:
            print("Class number index is: ",idxClassNumb)
            res = currLayer.dataProvider().deleteAttributes([idxClassNumb])
        # Commit the removal of fields.
        currLayer.updateFields()
        
    # Add the classification attributes.    
    if caps & QgsVectorDataProvider.AddAttributes:
        print("The layer supports addAttributes")
        
        # Add the classification attributes.
        res = currLayer.dataProvider().addAttributes(
        [QgsField("Class_Numb", QVariant.Int),
        QgsField("Class_Code", QVariant.String)])
        
    # Commit the addition of fields.
    currLayer.updateFields()

    #     Run the "CLASSIFY" function passing in the 
    #     working layer and the position of the classification
    #     attributes.
    idxClassNumb = fields.indexFromName('Class_Numb')
    idxClassCode = fields.indexFromName('Class_Code')
    classify(currLayer,idxClassNumb,idxClassCode)

    #     Run the "SUMMARY" function passing in the 
    #     working layer and the position of the classification
    #     attributes.
    idxShapeArea = fields.indexFromName('Shape_Area')
    summary(currLayer,idxClassNumb,idxClassCode, idxShapeArea)

# Mainline:  Start the script by invoking the MAIN function.
main()
