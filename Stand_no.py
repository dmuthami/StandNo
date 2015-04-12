######################################################################
## Update Stand No Script
## Attach script in ArcMap in a custom toolbox
## Run script as a script tool
##
##Challenge:Create Geoprocessing service for running on the web.

## Created by : dmuthami
## Updated : 12/04/2015
##
######################################################################

##  Compute Stand No
##  Select OBJECTID, Stand_No and Local_Authority ID Fields from a parcels feature class that participates in
##  parcel fabric
##  Need to obtain edit lock on the respective feature dataset/parcel fabric

##  Import ArcPy module: Provides access to ArcGIS powerful ArcObjects
##  Import sys module : module provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter
##  Import os modules: This module provides a portable way of using operating system dependent functionality e.g writing files
##  Import traceback :modules for debugging/ module provides a standard interface to extract, format and print stack traces of Python programs

import os, sys
import arcpy
import traceback
from arcpy import env

##Set the overwriteOutput environment setting to True
##Comment out line in script to overwrite data
#env.overwriteOutput = True

try:
    ##Obtain script parameter values
    ##objectid
    ##stand_no
    ##local_authority_id
    ##Feature Class of interest

    ##set workspace
    ##Acquire it as a parameter
    workspace=arcpy.GetParameterAsText(0)#Get from console or GUI being user input
    if workspace =='': #Checks if supplied parameter is null
        #Defaults to below hardcoded path if the parameter is not supplied. NB. May throw exceptions if it defaults to path below
        workspace=r"C:\DAVID-MUTHAMI\GIS Data\Namibia ULIMS\GIS\Datasource\Okahandja\Database\Okahandja\Okahandja.gdb"

    #workspace
    #Supports enterprise, file geodatabases
    env.workspace = workspace

    ##Local Authority Parcels Feature Class of interest
	##Acquire it as a parameter
    featureClass = arcpy.GetParameterAsText(1)#Get from console or GUI being user input
    if featureClass == "":#Checks if supplied parameter is null
        featureClass="okahandja_Parcels"#Defaults to okahandja_Parcels part of a parcel fabric.Nb. May throw unnecessary exceptions and tool may fail

    ##Objectid field
	##Acquire it as a parameter
    objectID_fieldName=arcpy.GetParameterAsText(2)#Get from console or GUI being user input
    if objectID_fieldName == '':#Checks if supplied parameter is null
        objectID_fieldName="OBJECTID" #Defaults to OBJECTID.

    ##StandNo field
	##Acquire it as a parameter
    standNo_fieldName = arcpy.GetParameterAsText(3)#Get from console or GUI being user input
    if standNo_fieldName == "": #Checks if supplied parameter is null
        standNo_fieldName="oh_stand_no" #Defaults to OBJECTID.Nb. May throw unnecessary exceptions and tool may fail

    ##SLocal_authority ID
	##Acquire it as a parameter
    local_authority_id_fieldName = arcpy.GetParameterAsText(4)#Get from console or GUI being user input
    if local_authority_id_fieldName == "":#Checks if supplied parameter is null
        local_authority_id_fieldName="oh_local_authority_id" #Defaults to oh_local_authority_id.Nb. May throw unnecessary exceptions and tool may fail

    ##------------------------------------------------------------------------------------
    ##------------------Beginning of Functions--------------------------------------------

    ##Functions creates stand no
    ##argument:local_authority_id ID of the local authority
    ##argument:object_id unique autoincrementing field in the feature clocal_authority_idss
    def createStandNo(local_authority_id, object_id):
        #Stand_No is initially empty;
        stand_no =""#initialize to null

        #pass local_authority_id argument from function to local variable and cast to string
        local_authority_id = str(local_authority_id)
        object_id = str(object_id)#pass object_id argument from function to local variable and cast to string

        local_authority_id_length = 3 # local authority value is deemed not to exceed 999 and thus the need to set the len to 3
        object_id_length = 7 # object id value is deemed not to exceed 9 999 999 and thus the need to set the len to 7

        #Compare the length of the item (local authority) and add zeros infron if the length is less than specified
        if(len(local_authority_id) < local_authority_id_length):
            #function called to return stand number with object id and additional zeroes
            stand_no = returnZeros(local_authority_id_length-len(local_authority_id)) + local_authority_id
        else:
            stand_no += local_authority_id #concatenate without prefixing with zeroes

        #Compare the length of the item (objectid) and add zeros infron if the length is less than specified
        if(len(object_id) < object_id_length):
            #function called to return stand number with object id and additional zeroes
            stand_no += returnZeros(object_id_length-len(object_id)) + object_id
        else:
            stand_no += object_id #concatenate without prefixing with zeroes

        #Return the concatenated stand_no
        return stand_no

    ##Functions prefixing zeros
    ##argument:num /number of zeroes to prefix
    ##argument:object_id unique autoincrementing field in the feature class
    def returnZeros(num):
        #If the value of required zeros is one, return, otherwise loop through
        v = "0" #String holding the character elements for zero. By default intialized with one zero
        count = 1 #manages/control or serves as an exit mechanis to the indeterminate while loop

        while (count < num): #Condition for loop. loop exits if count is equal or greater than number
            #print "num: %s cnt %s"%(num,count)
            #print count
            v += "0"
            count = count + 1 #Increment count by one every cycle
        return v #Return prefixing zeroes

    ##----------------------End of Functions--------------------------------------------------------
    ##----------------------------------------------------------------------------------------------
    ##---------------------------------Edit Session code Starts from here---------------------------

    ## We want to determine if the input features are fields or the are strings. Checking with StandNo only
    ## Define array objects for Fields
    ## Remember they are user defined and arguments captured by the user

    ##Custom Error Handling
    ## This shall be done later

    #---Custom code to come in here later----------------

    fields = (standNo_fieldName,objectID_fieldName, local_authority_id_fieldName)

    update_stand_no = "";#initialize variable to string of length zero

    #SQL expression to select only the stand numbers that are null
    SQLExp = standNo_fieldName + " is Null"

    # Start an edit session. Must provide the worksapce.
    edit = arcpy.da.Editor(env.workspace)

    # Edit session is started without an undo/redo stack for versioned data
    #  (for second argument, use False for unversioned data)
    #Compulsory for above feature class participating in a complex data such as parcel fabric
    edit.startEditing(False, True)

    # Start an edit operation
    edit.startOperation()

    #Update cursor goes here
    with arcpy.da.UpdateCursor(featureClass, fields,SQLExp) as cursor:
        for row in cursor:# loops per record in the recordset and returns an aray of objects
            #Call functions below compute stand no
            update_stand_no = createStandNo(row[2],row[1])
            row[0] = str(update_stand_no)  #Read area value as double
            # Update the cursor with the updated row object that contains now the new record
            cursor.updateRow(row)

    # Stop the edit operation.
    edit.stopOperation()

    # Stop the edit session and save the changes
    #Compulsory for release of locks arising from edit session. NB. Sigleton principle is observed here
    edit.stopEditing(True)
    #-----------------------------------Edit Session ends here---------------------------------

    #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).
    arcpy.AddMessage('Computation of Stand No\'s is complete')

    ##Commented since it was being used for debug mode
    #print('Editing is complete for all stand numbers')

except:
    ## Return any Python specific errors and any error returned by the geoprocessor
    ##
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
            str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
    msgs = "Geoprocesssing  Errors :\n" + arcpy.GetMessages(2) + "\n"

    ##dd custom informative message to the Python script tool
    arcpy.AddError(pymsg) #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).
    arcpy.AddError(msgs)  #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).

    ##For debugging purposes only
    ##To be commented on python script
    print pymsg
    print "\n" +msgs

