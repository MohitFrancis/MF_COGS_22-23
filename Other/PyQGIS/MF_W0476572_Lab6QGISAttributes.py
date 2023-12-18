'''
    Program   : MF_W0476572_Lab6QGISAttributes.py
    Programmer: Mohit Francis
    Date      : 01 November 2022
    Purpose   : PROG 5000: Lab 6 - QGIS and Attributes
'''

## Import the GUI library for dialog box.
from PyQt5.QtGui import *

## Set a variable to the active layer in the Layers window pane.
currLayer = qgis.utils.iface.activeLayer()

## Using for loop, create list storing names of fields
## if fields contain string variables.
fieldStrList = []
for field in currLayer.fields():
    if field.typeName() == 'String':
        fieldStrList.append(field.name())

## Creating selection list by combining field names 
## from fieldStrList with incrementing option numbers
## to create a list of numbered field names for use in selection label.
optionCount = 0
selectionList = []
for field in fieldStrList:
    optionCount += 1
    selectionList.append(str(optionCount) + ". " + field)

## Creating selection label for GUI dialog using simple
## 'for loop' to pick elements from selectionList
## and combine them into one long string.
## (I could combine this loop with the loop in lines 23 to 27
## but I moved this portion of the code so it looks cleaner;
## the previous version used lots of string functions and it looked ugly).
lblDialog = ""
for element in selectionList:
    lblDialog = lblDialog + element + "\n"
    
## Initialise dialog.
qid = QInputDialog()

## Set dialog attributes.
title = "Enter Option No. To Select Attribute Name From Layer"
label = lblDialog
mode = QLineEdit.Normal
default = "1"

## Execute dialog.
attrNo, ok = QInputDialog.getText(qid, title, label, mode, default)

goodNum = False

while goodNum == False:
    try:
        int(attrNo)
        goodNum = True
    except:
        goodNum = False
        print("Please enter a number relating to the list of options.")


## User inputs a number matching the given options from dialog.
## This number is minused. The result is used to index list of
## fields from active layer to select field name from layer.
attrName = fieldStrList[int(attrNo) - 1]
    
print ("You chose the field '%s'" % attrName)

## Create empty lists to store all values and
## all unique values from selected field.
listValues = []
listUniqueValues = []

try:
    ## Search for selected field name
    ## within the list of field names fieldStrList.
    position = fieldStrList.index(attrName)
    
    ## Count the number of rows/records/features
    ## in selected field.
    numOfFeatures = currLayer.featureCount()
    
    ## Simple 'for loop' to create two lists: one to store all values of features
    ## within chosen field and one to store all unique values within chosen field.
    for nums in range(numOfFeatures):
        ## Get current features first
        currFeature = currLayer.getFeature(nums)
        
        ## Append listValues with all values of features from field.
        listValues.append(currFeature [attrName])
        
        ## Find unique values and add to a list of unique values.
        if currFeature [attrName] in listUniqueValues:
            listUniqueValues
        else:
        ## If value currently checked does not within listUniqueValues,
        ## then append value to list of unique values.
            listUniqueValues.append(currFeature [attrName])
    
    ## Formatted print statement to print list of unique values within chosen field.
    print ("The list of unique values within field '%s' are %s." % (attrName, listUniqueValues))
    
    ## Use list comprehension to count all occurrences of values within list of all values
    ## of values within list of unique values.
    countList = [(element,listValues.count(element)) for element in listUniqueValues]
    
    ## Display formatted print statement(s) of number of occurrences of unique values
    ## by indexing tuples within the list.
    for i in countList:
        print("The number of occurrence(s) of unique value '%s' in field '%s' is %i." % (i[0], attrName, i[1]))
    
except:
    ## If search for selected field name within the list of field names fieldStrList fails,
    ## print this formatted error message.
    print ("The option no. '%i' does not relate to a field in %s" % (attrNo, currLayer.name()))
